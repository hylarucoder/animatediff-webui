import logging

from safetensors.torch import load_file

from animatediff import get_dir
from animatediff.utils.lora_diffusers import LoRANetwork, create_network_from_weights

logger = logging.getLogger(__name__)

data_dir = get_dir("data")


def merge_safetensors_lora(text_encoder, unet, lora_path, alpha=0.75, is_animatediff=True):
    sd = load_file(lora_path)

    print(f"create LoRA network")
    lora_network: LoRANetwork = create_network_from_weights(
        text_encoder, unet, sd, multiplier=alpha, is_animatediff=is_animatediff
    )
    print(f"load LoRA network weights")
    lora_network.load_state_dict(sd, False)
    lora_network.merge_to(alpha)


def load_lora_map(pipe, lora_map_config, video_length):
    new_map = {}
    for item in lora_map_config:
        lora_path = data_dir.joinpath(item)
        if type(lora_map_config[item]) in (float, int):
            merge_safetensors_lora(pipe.text_encoder, pipe.unet, lora_path, lora_map_config[item], True)
        else:
            new_map[lora_path] = lora_map_config[item]

    lora_map = LoraMap(pipe, new_map, video_length)
    pipe.lora_map = lora_map if lora_map.is_valid else None


class LoraMap:
    def __init__(
        self,
        pipe,
        lora_map,
        video_length,
    ):
        self.networks = []

        def create_schedule(scales, length):
            scales = {int(i): scales[i] for i in scales}
            keys = sorted(scales.keys())

            if len(keys) == 1:
                return {i: scales[keys[0]] for i in range(length)}
            keys = keys + [keys[0]]

            schedule = {}

            def calc(rate, start_v, end_v):
                return start_v + (rate * rate) * (end_v - start_v)

            for key_prev, key_next in zip(keys[:-1], keys[1:]):
                v1 = scales[key_prev]
                v2 = scales[key_next]
                if key_prev > key_next:
                    key_next += length
                for i in range(key_prev, key_next):
                    dist = i - key_prev
                    if i >= length:
                        i -= length
                    schedule[i] = calc(dist / (key_next - key_prev), v1, v2)
            return schedule

        for lora_path in lora_map:
            sd = load_file(lora_path)
            if not sd:
                continue
            lora_network: LoRANetwork = create_network_from_weights(
                pipe.text_encoder, pipe.unet, sd, multiplier=0.75, is_animatediff=True
            )
            lora_network.load_state_dict(sd, False)
            lora_network.apply_to(0.75)

            self.networks.append(
                {
                    "network": lora_network,
                    "region": lora_map[lora_path]["region"],
                    "schedule": create_schedule(lora_map[lora_path]["scale"], video_length),
                }
            )

        def region_convert(i):
            if i == "background":
                return 0
            else:
                return int(i) + 1

        for net in self.networks:
            net["region"] = [region_convert(i) for i in net["region"]]

        #        for n in self.networks:
        #            logger.info(f"{n['region']=}")
        #            logger.info(f"{n['schedule']=}")

        if self.networks:
            self.is_valid = True
        else:
            self.is_valid = False

    def to(
        self,
        device,
        dtype,
    ):
        for net in self.networks:
            net["network"].to(device=device, dtype=dtype)

    def apply(
        self,
        cond_index,
        cond_nums,
        frame_no,
    ):
        """
        neg 0 (bg)
        neg 1
        neg 2
        pos 0 (bg)
        pos 1
        pos 2
        """

        region_index = cond_index if cond_index < cond_nums // 2 else cond_index - cond_nums // 2
        #        logger.info(f"{cond_index=}")
        #        logger.info(f"{cond_nums=}")
        #        logger.info(f"{region_index=}")

        for i, net in enumerate(self.networks):
            if region_index in net["region"]:
                scale = net["schedule"][frame_no]
                if scale > 0:
                    net["network"].active(scale)
                #                    logger.info(f"{i=} active {scale=}")
                else:
                    net["network"].deactive()
            #                    logger.info(f"{i=} DEactive")

            else:
                net["network"].deactive()

    #               logger.info(f"{i=} DEactive")

    def unapply(
        self,
    ):
        for net in self.networks:
            net["network"].deactive()

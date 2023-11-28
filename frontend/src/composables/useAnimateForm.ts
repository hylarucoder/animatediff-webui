import { aspect_ratios, performances, type TPreset } from "~/composables/useStore"

type TLoRA = {
  name: string | null;
  weight: number;
}

const form = ref<
  {
    checkpoint: string;
    motion: string;
    performance: string;
    aspect_ratio: string;
    duration: number;
    seed: number;
    head_prompt: string;
    tail_prompt: string;
    negative_prompt: string;
    preset: string;
    fps: number;
    project: string;
    motion_lora: string[];
    loras: TLoRA[];
  }
>({
  checkpoint: "",
  motion: "",
  performance: performances[0],
  aspect_ratio: aspect_ratios[3],
  duration: 4,
  seed: -1,
  head_prompt: "",
  tail_prompt: "",
  negative_prompt: "",
  preset: "",
  fps: 8,
  project: "001-demo",
  motion_lora: [],
  loras: [
    {
      name: null,
      weight: 0.7,
    },
    {
      name: null,
      weight: 0.7,
    },
    {
      name: null,
      weight: 0.7,
    },
    {
      name: null,
      weight: 0.7,
    },
    {
      name: null,
      weight: 0.7,
    },
  ],
},
)

export const useAnimateForm = () => {
  return {
    form,
    setPreset: (preset: TPreset) => {
      console.log("---> set preset", preset)
      form.value.checkpoint = preset.checkpoint
      form.value.motion = preset.motion
      form.value.loras = (preset.loras || []).map((x) => {
        return {
          name: x[0],
          weight: x[1],
        }
      })
      form.value.motion_lora = preset.motion_lora
      form.value.performance = preset.performance
      form.value.aspect_ratio = preset.aspect_ratio
      form.value.head_prompt = preset.head_prompt
      form.value.tail_prompt = preset.tail_prompt
      form.value.negative_prompt = preset.negative_prompt
    },
  }
}

import type { UnwrapRef } from "vue"
import { convertToTimeString } from "~/utils/t"

interface FormState {
  ipAdapter: string[]
  controlnet: string[]
}

const duration = 12
const fps = 8
const unitWidth = 25
const blocks = new Map<number, string>([])

const millisecondStep = 1000 / fps

for (let i = 0; i < millisecondStep * duration * fps; i += millisecondStep) {
  if (i % 1000 !== 0) {
    continue
  }
  // start and duration
  blocks.set(i, convertToTimeString(i))
}

const promptLayer = {
  title: "prompt",
  blocks,
}

const timeline: UnwrapRef<FormState> = reactive({
  ipAdapter: ["ipadapter"],
  controlnet: ["controlnet_openpose", "controlnet_depth"],
})

const controlnets = [
  "controlnet_canny",
  "controlnet_depth",
  "controlnet_inpaint",
  "controlnet_ip2p",
  "controlnet_lineart",
  "controlnet_lineart_anime",
  "controlnet_mlsd",
  "controlnet_normalbae",
  "controlnet_openpose",
  "controlnet_scribble",
  "controlnet_seg",
  "controlnet_shuffle",
  "controlnet_softedge",
  "controlnet_tile",
]

const timelines = ref([
  {
    title: "ip-adapter",
    slug: "ip-adapter",
    blocks,
  },
  ...controlnets.map((x) => {
    const a = x.replaceAll("controlnet_", "")
    return {
      title: a,
      slug: a,
      blocks,
    }
  }),
])

export const useTimeline = () => {
  return {
    fps,
    unitWidth,
    duration,
    promptLayer,
    timeline,
    timelines,
  }
}

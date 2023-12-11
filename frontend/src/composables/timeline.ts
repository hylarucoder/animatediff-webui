import type { UnwrapRef } from "vue"
import type { TPromptBlock } from "~/composables/options"

interface FormState {
  ipAdapter: string[]
  controlnet: string[]
}

export interface TTrackBlock {
  start: number
  duration: number
  prompt: string
}

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

export const useTimelineStore = defineStore("timeline", () => {
  const refTimeline = ref(null)
  const { isOutside: isMouseOutside } = useMouseInElement(refTimeline, {})
  const refRuler = ref(null)
  const { elementX: rulerPos } = useMouseInElement(refRuler, {})
  const timeline: UnwrapRef<FormState> = reactive({
    ipAdapter: ["ipadapter"],
    controlnet: ["controlnet_openpose", "controlnet_depth"],
  })
  const optTimelines = computed(() => {
    const intersection = timeline.controlnet.filter((value) => timeline.controlnet.includes(value))
    return tracks.value.filter((timeline) => intersection.includes(timeline.slug))
  })

  const promptBlocks = ref<TPromptBlock[]>([])
  const duration = ref(12)
  const fps = ref(8)
  const unitWidth = ref(25)
  const unit = computed(() => {
    return Math.floor(1000 / unitWidth.value)
  })
  const unitStep = computed(() => {
    return 1000 / fps.value
  })
  const blocks = ref<TTrackBlock[]>([])

  const initBlocks = () => {
    const _blocks = []
    // TODO: magic
    for (let i = 0; i < unitStep.value * 12 * fps.value; i += unitStep.value) {
      if (i % 1000 !== 0) {
        continue
      }
      // start and duration
      _blocks.push({
        // 毫秒
        start: i,
        duration: 125,
        prompt: "",
      })
    }
    blocks.value = _blocks
  }

  const promptTrack = {
    title: "prompt",
    blocks,
  }
  const tracks = ref([
    {
      title: "ip-adapter",
      slug: "ip-adapter",
      blocks,
    },
    ...controlnets.map((x) => {
      const a = x.replaceAll("controlnet_", "")
      return {
        title: a,
        slug: x,
        blocks,
      }
    }),
  ])
  const addPromptBlocks = (block: TPromptBlock) => {
    promptBlocks.value.push(block)
  }
  const hasPromptBlocks = (start: number) => {
    const starts = promptBlocks.value.map((x) => {
      return x.start
    })
    return starts.includes(start)
  }
  const removePromptBlocks = (start: number) => {
    promptBlocks.value = promptBlocks.value.filter((x) => {
      return x.start !== start
    })
  }
  const leftPanelWidth = ref(100)
  return {
    refRuler,
    leftPanelWidth,
    promptBlocks,
    rulerPos,
    isMouseOutside,
    refTimeline,
    fps,
    unit,
    unitStep,
    unitWidth,
    duration,
    promptTrack,
    timeline,
    tracks,
    optTimelines,
    initBlocks,
    addPromptBlocks,
    hasPromptBlocks,
    removePromptBlocks,
  }
})

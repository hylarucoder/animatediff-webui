import { getOptions } from "~/client"

export interface TPromptBlock {
  start: number
  duration: number
  prompt: string
}

export interface TPreset {
  name: string
  performance: string
  aspectRatio: string
  prompt: string
  promptBlocks: TPromptBlock[]
  highRes: boolean
  negativePrompt: string
  checkpoint: string
  loras: (null | number | string)[][]
  motion: string
  motionLora?: any
  fps: number
  duration: number
  seed: number
  lcm: boolean
  sampler: string
  step: number
  cfg: number
}

export interface TCheckpoint {
  name: string
  thumbnail: string
}

export interface TOptions {
  projects: string[]
  checkpoints: TCheckpoint[]
  loras: TCheckpoint[]
  motions: TCheckpoint[]
  motionLoras: TCheckpoint[]
  presets: TPreset[]
  aspectRatios: string[]
  performances: string[]
}

export const aspectRatios = ["768x432 | 16:9", "768x576 | 4:3", "600x600 | 1:1", "432x768 | 9:16", "576x768 | 3:4"]

const performanceMapping = new Map([
  ["Speed", "SPEED"],
  ["Quality", "QUALITY"],
  ["Extreme Speed", "EXTREME_SPEED"],
])
export const performances = [...performanceMapping.keys()]

export const useFormStore = defineStore("form", () => {
  const videoUrl = ref("")
  const videoStatus = ref("")
  const checkpoint = ref("")
  const performance = ref(performances[0])
  const motion = ref("")
  const aspectRatio = ref(aspectRatios[3])
  const highRes = ref(false)
  const duration = ref(4)
  const seed = ref(-1)
  const prompt = ref("")
  const negativePrompt = ref("")
  const preset = ref("default")
  const fps = ref(8)
  const project = ref("001-demo")
  const motionLora = ref([])
  const loras = ref([
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
  ])
  const { promptBlocks } = storeToRefs(useTimeline())
  const loadPreset = (_preset: TPreset) => {
    preset.value = _preset.name
    checkpoint.value = _preset.checkpoint
    motion.value = _preset.motion
    loras.value = (_preset.loras || []).map((x) => {
      return {
        name: x[0],
        weight: x[1],
      }
    })

    motionLora.value = _preset.motionLora
    performance.value = _preset.performance
    aspectRatio.value = _preset.aspectRatio
    prompt.value = _preset.prompt
    negativePrompt.value = _preset.negativePrompt
    fps.value = _preset.fps
    duration.value = _preset.duration
    promptBlocks.value = _preset.promptBlocks
  }
  return {
    videoUrl,
    videoStatus,
    checkpoint,
    highRes,
    motion,
    performance,
    aspectRatio,
    duration,
    seed,
    prompt,
    negativePrompt,
    preset,
    fps,
    project,
    motionLora,
    loras,
    promptBlocks,
    loadPreset,
  }
})

const unflatten = (arr: any[]) => {
  return arr.map((x) => {
    return {
      label: x,
      value: x,
    }
  })
}

const cleanLabel = (f: string) => {
  if (f.endsWith(".safetensors")) {
    return f.split(".safetensors")[0]
  }
  return f
}

const unflattenCheckpoint = (arr: any[]) => {
  return arr.map((x) => {
    return {
      label: cleanLabel(x.name),
      value: x.name,
      thumbnail: x.thumbnail,
    }
  })
}

function unflattenKV(map) {
  return Array.from(map, ([label, value]) => ({ label, value }))
}

export const useOptionsStore = defineStore("options", () => {
  const options = ref<TOptions>({
    projects: [],
    checkpoints: [],
    loras: [],
    motions: [],
    motionLoras: [],
    presets: [],
    aspectRatios,
    performances,
  })
  const form = useFormStore()
  const { loadPreset } = form
  const optionLoaded = ref(true)
  const optPerformances = computed(() => {
    return unflattenKV(performanceMapping)
  })
  const optAspectRadios = computed(() => {
    return unflatten(aspectRatios)
  })
  const optCheckpoints = computed(() => {
    return unflattenCheckpoint(options.value.checkpoints)
  })
  const optLoras = computed(() => {
    return unflattenCheckpoint(options.value.loras)
  })
  const optMotions = computed(() => {
    return unflattenCheckpoint(options.value.motions)
  })
  const optMotionLoras = computed(() => {
    return unflattenCheckpoint(options.value.motionLoras)
  })
  const optPresets = computed(() => {
    return unflattenCheckpoint(options.value.presets)
  })
  const optProjects = computed(() => {
    return unflatten(options.value.projects)
  })
  const loadOptions = (_options) => {
    options.value.presets = _options.presets
    options.value.projects = _options.projects
    options.value.checkpoints = _options.checkpoints
    options.value.loras = _options.loras
    options.value.motions = _options.motions
    options.value.motionLoras = _options.motionLoras
  }
  const init = async () => {
    const res = await getOptions()
    loadOptions(res)
    const preset_name = res.presets[0].name
    const _preset = res.presets.find((p) => p.name === preset_name)
    loadPreset(_preset)
  }

  return {
    optionLoaded,
    options,
    optProjects,
    optPresets,
    optPerformances,
    optAspectRadios,
    optCheckpoints,
    optLoras,
    optMotions,
    optMotionLoras,
    loadOptions,
    init,
  }
})

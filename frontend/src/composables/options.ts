import { getOptions } from "~/client"
import { ensureSpaceAfterComma } from "~/utils/t"

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
  cameraControl: any
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
  cameraControl: any
  presets: TPreset[]
  aspectRatios: string[]
  performances: string[]
}

// export const aspectRatios = ["768x432 | 16:9", "768x576 | 4:3", "600x600 | 1:1", "432x768 | 9:16", "576x768 | 3:4"]
export const aspectRatios = ["16:9", "4:3", "1:1", "9:16", "3:4"]

const performanceMapping = new Map([
  ["Speed", "SPEED"],
  ["Quality", "QUALITY"],
  ["Extreme Speed", "EXTREME_SPEED"],
])
export const performances = [...performanceMapping.keys()]

const x2res = (res: string) => {
  const arr = res.split("x")
  return parseInt(arr[0]) * 2 + "x" + parseInt(arr[1]) * 2
}

const calcSizeOpts = (v) => {
  const ar = {
    "16:9": "768x432",
    "4:3": "768x576",
    "1:1": "600x600",
    "3:4": "576x768",
    "9:16": "432x768",
  }[v]
  return [
    {
      label: ar,
      value: ar,
    },
    {
      label: x2res(ar),
      value: x2res(ar),
    },
  ]
}

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
  const cameraControl = ref({
    panLeft: 0,
    panRight: 0,
    rollingAnticlockwise: 0,
    rollingClockwise: 0,
    tileDown: 0,
    tileUp: 0,
    zoomIn: 0,
    zoomOut: 0,
  })
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
  const { promptBlocks } = storeToRefs(useTimelineStore())
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

    cameraControl.value = _preset.cameraControl
    performance.value = _preset.performance
    aspectRatio.value = _preset.aspectRatio
    prompt.value = ensureSpaceAfterComma(_preset.prompt)
    negativePrompt.value = ensureSpaceAfterComma(_preset.negativePrompt)
    fps.value = _preset.fps
    duration.value = _preset.duration
    promptBlocks.value = _preset.promptBlocks
  }
  const c = calcSizeOpts(aspectRatio.value)
  const sizeOpts = ref(c)
  const size = ref(c[0].value)
  watch(aspectRatio, (v) => {
    const c = calcSizeOpts(v)
    sizeOpts.value = c
    size.value = c[0].value
  })
  watch(size, (v) => {
    highRes.value = v === sizeOpts.value?.[1]?.value
  })
  return {
    size,
    sizeOpts,
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
    cameraControl,
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
  return Array.from(map, ([label, value]) => ({
    label,
    value,
  }))
}

export const useOptionsStore = defineStore("options", () => {
  const options = ref<TOptions>({
    projects: [],
    checkpoints: [],
    loras: [],
    cameraControl: {},
    motions: [],
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
    options.value.cameraControl = _options.cameraControl
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
    loadOptions,
    init,
  }
})

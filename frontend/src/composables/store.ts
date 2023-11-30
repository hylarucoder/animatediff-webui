import { urlPrefix } from "~/consts"
import { TStatus } from "~/composables/usePlayer"

export interface TPreset {
  name: string
  performance: string
  aspect_ratio: string
  head_prompt: string
  tail_prompt: string
  negative_prompt: string
  checkpoint: string
  loras?: (null | number | string)[][]
  motion: string
  motion_lora?: any
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
  motion_loras: TCheckpoint[]
  presets: TPreset[]
  aspect_ratios: string[]
  performances: string[]
}

export const aspect_ratios = ["768x432 | 16:9", "768x576 | 4:3", "600x600 | 1:1", "432x768 | 9:16", "576x768 | 3:4"]

export const performances = ["Speed", "Quality", "Extreme Speed"]
const checkpoint = ref("")
const motion = ref("")
const performance = ref(performances[0])
const aspect_ratio = ref(aspect_ratios[3])
const duration = ref(4)
const seed = ref(-1)
const head_prompt = ref("")
const tail_prompt = ref("")
const negative_prompt = ref("")
const preset = ref("")
const fps = ref(8)
const project = ref("001-demo")
const motion_lora = ref([])
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
  motion_lora.value = _preset.motion_lora
  performance.value = _preset.performance
  aspect_ratio.value = _preset.aspect_ratio
  head_prompt.value = _preset.head_prompt
  tail_prompt.value = _preset.tail_prompt
  negative_prompt.value = _preset.negative_prompt
}
const video_url = ref("")
const video_status = ref("")
const pullStatus = async () => {
  const res = (await $fetch(urlPrefix + "/api/render/status")) as any
  if (!res.video_path) {
    return
  }
  video_url.value = urlPrefix + "/media?path=" + res.video_path
  video_status.value = TStatus.SUCCESS
  // reloadVideo()
  // player.video_url.value = urlPrefix + "/media?path=" + res.video_path
  // player.status.value = TStatus.SUCCESS
  // player.reloadVideo()
}
// fetch options from api

export const useFormStore = () => {
  return {
    video_url,
    video_status,
    checkpoint,
    motion,
    performance,
    aspect_ratio,
    duration,
    seed,
    head_prompt,
    tail_prompt,
    negative_prompt,
    preset,
    fps,
    project,
    motion_lora,
    loras,
    loadPreset,
  }
}

const unflatten = (arr: any[]) => {
  return arr.map((x) => {
    return {
      label: x,
      value: x,
    }
  })
}

const unflattenCheckpoint = (arr: any[]) => {
  return arr.map((x) => {
    return {
      label: x.name,
      value: x.name,
    }
  })
}

const options = ref<TOptions>({
  projects: [],
  checkpoints: [],
  loras: [],
  motions: [],
  motion_loras: [],
  presets: [],
  aspect_ratios,
  performances,
})

export const useOptionsStore = () => {
  const optionLoaded = ref(true)
  // const form = useFormStore()
  // const { preset } = form
  const optPerformances = computed(() => {
    return unflatten(performances)
  })
  const optAspectRadios = computed(() => {
    return unflatten(aspect_ratios)
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
    return unflattenCheckpoint(options.value.motion_loras)
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
    options.value.motion_loras = _options.motion_loras
  }
  const init = async () => {
    const res = (await $fetch(urlPrefix + `/api/options`)) as any
    loadOptions(res)
    const preset_name = res.presets[2].name
    console.log("init=>", preset_name)
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
}

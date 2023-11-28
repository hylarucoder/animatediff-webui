import { create } from "zustand"

export interface TPreset {
  name: string
  performance: string
  aspect_ratio: string
  head_prompt: string
  tail_prompt: string
  negative_prompt: string
  checkpoint: string
  loras?: (null | number | number | string)[][][]
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

interface TCheckpoint {
  name: string
  thumbnail: string
}

interface TOptions {
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

export const useStore = create<TOptions>((set) => ({
  projects: [],
  checkpoints: [],
  loras: [],
  motions: [],
  motion_loras: [],
  presets: [],
  aspect_ratios: aspect_ratios,
  performances: performances,
  setOptions: (_options: TOptions) => {
    set({
      presets: _options.presets,
      projects: _options.projects,
      checkpoints: _options.checkpoints,
      loras: _options.loras,
      motions: _options.motions,
      motion_loras: _options.motion_loras,
    })
  },
}))

export enum TStatus {
  PENDING = "PENDING",
  LOADING = "LOADING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

export const usePlayer = create((set) => ({
  status: TStatus.PENDING,
  video_url: "",
  reloadVideo: () => {
    // console.log(videoRef, videoRef?.value)
    // videoRef?.value?.load()
  },
}))

type TLoRA = {
  name: string | null
  weight: number
}
type TForm = {
  checkpoint: string
  motion: string
  performance: string
  aspect_ratio: string
  duration: number
  seed: number
  head_prompt: string
  tail_prompt: string
  negative_prompt: string
  preset: string
  fps: number
  project: string
  motion_lora: string[]
  loras: TLoRA[]
}

export const useAnimateForm = create<TForm>((set) => ({
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
  settingsFormFields: [
    { name: ["performance"], value: "Speed" },
    { name: ["aspect_ratio"], value: "768x432 | 16:9" },
  ],
  setSettingsFormFields: (fields) => {
    set({
      settingsFormFields: fields,
    })
  },
  topbarFormFields: [
    { name: ["preset"], value: "" },
    { name: ["project"], value: "" },
  ],
  setTopbarFormFields: (fields) => {
    set({
      topbarFormFields: fields,
    })
  },
  setPreset: (preset: TPreset) => {
    set({
      checkpoint: preset.checkpoint,
      motion: preset.motion,
      performance: preset.performance,
      aspect_ratio: preset.aspect_ratio,
      head_prompt: preset.head_prompt,
      tail_prompt: preset.tail_prompt,
      negative_prompt: preset.negative_prompt,
      motion_lora: preset.motion_lora,
      fps: preset.fps,
      duration: preset.duration,
      seed: preset.seed,
      loras: preset.loras.map((x) => {
        return {
          name: x[0],
          weight: x[1],
        }
      }),
    })
    set({
      settingsFormFields: [
        { name: ["performance"], value: preset.performance },
        { name: ["aspect_ratio"], value: preset.aspect_ratio },
      ],
    })
  },
}))

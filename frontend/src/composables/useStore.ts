export interface TPreset {
  name: string;
  performance: string;
  aspect_ratio: string;
  head_prompt: string;
  tail_prompt: string;
  negative_prompt: string;
  checkpoint: string;
  loras?: (null | number | number | string)[][][];
  motion: string;
  motion_lora?: any;
  fps: number;
  duration: number;
  seed: number;
  lcm: boolean;
  sampler: string;
  step: number;
  cfg: number;
}

interface TCheckpoint {
  name: string;
  thumbnail: string;
}

interface TOptions {
  projects: string[];
  checkpoints: TCheckpoint[];
  loras: TCheckpoint[];
  motions: TCheckpoint[];
  motion_loras: TCheckpoint[];
  presets: TPreset[];
  aspect_ratios: string[];
  performances: string[];
}

export const aspect_ratios = [
  "768x432 | 16:9",
  "768x576 | 4:3",
  "600x600 | 1:1",
  "432x768 | 9:16",
  "576x768 | 3:4",
]

export const performances = [
  "Speed",
  "Quality",
  "Extreme Speed",
]
const options = ref<TOptions>({
  projects: [],
  checkpoints: [],
  loras: [],
  motions: [],
  motion_loras: [],
  presets: [],
  aspect_ratios: aspect_ratios,
  performances: performances,
})

export const useStore = () => {

  return {
    options,
    setOptions: (_options: TOptions) => {
      options.value.presets = _options.presets
      options.value.projects = _options.projects
      options.value.checkpoints = _options.checkpoints
      options.value.loras = _options.loras
      options.value.motions = _options.motions
      options.value.motion_loras = _options.motion_loras
      console.log("set optons", toRaw(options.value.presets))
    },
  }
}

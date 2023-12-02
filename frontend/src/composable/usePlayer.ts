export enum TStatus {
  PENDING = "PENDING",
  LOADING = "LOADING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

const video_url = ref("")
const status = ref(TStatus.PENDING)
const videoRef = ref<HTMLVideoElement | null>(null)

type TProgress = {
  description: string
  completed: number
  total: number
}

const progress = ref<{
  main: TProgress
  tasks: TProgress[]
}>({
  main: {
    description: "progressing",
    completed: 10,
    total: 100,
  },
  tasks: [],
})

export const usePlayer = () => {
  return {
    status,
    video_url,
    videoRef,
    progress,
    reloadVideo: () => {
      videoRef?.value?.load()
    },
  }
}

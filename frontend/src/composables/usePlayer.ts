export enum TStatus {
  PENDING = "PENDING",
  LOADING = "LOADING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

const video_url = ref("")
const status = ref(TStatus.PENDING)
const videoRef = ref<HTMLVideoElement | null>(null)
const tasks = ref<
  {
    description: string
    completed: number
    total: number
  }[]
>([])

export const usePlayer = () => {
  return {
    status,
    video_url,
    videoRef,
    tasks,
    reloadVideo: () => {
      console.log(videoRef, videoRef?.value)
      videoRef?.value?.load()
    },
  }
}

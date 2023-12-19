import { formatProxyMedia, getTaskStatus, submitTask } from "~/client"

export enum TStatus {
  PENDING = "PENDING",
  RUNNING = "RUNNING",
  LOADING = "LOADING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

type TSubtask = {
  status: TStatus
  description: string
  completed: number
  total: number
  videoPath: string
}

type TOverallTask = {
  pid: number
  status: TStatus
  completed: number
  total: number
  videoPath: string
  subtasks: TSubtask[]
}

export const useVideoExportStore = defineStore("videoExport", () => {
  const modalVisible = ref(false)
  const formStore = useFormStore()
  const timelineStore = useTimelineStore()
  const { promptBlocks } = timelineStore
  const videoPlayerStore = useVideoPlayer()
  const task = ref<TOverallTask>({
    pid: 0,
    status: TStatus.PENDING,
    completed: 0,
    total: 100,
    videoPath: "",
    subtasks: [],
  })
  const showModal = () => {
    modalVisible.value = true
  }
  const hideModal = () => {
    modalVisible.value = false
  }

  const { pause, resume, isActive } = useIntervalFn(async () => {
    const res = (await getTaskStatus({
      pid: task.value.pid,
    })) as TOverallTask
    if (!res?.pid) {
      task.value.status = TStatus.ERROR
      return
    }
    task.value.pid = res.pid
    task.value.status = res.status
    task.value.completed = res.completed
    task.value.total = res.total
    task.value.subtasks = res.subtasks.filter((x) => x.completed > 0)

    if (!res?.videoPath) {
      return
    }
    task.value.videoPath = res.videoPath
    videoPlayerStore.loadVideo(formatProxyMedia(res.videoPath))
    hideModal()
    // player.reloadVideo()
    pause()
  }, 2000)
  onMounted(() => pause())

  const submitExport = async () => {
    task.value.pid = 0
    task.value.status = TStatus.PENDING
    task.value.completed = 0
    task.value.total = 100
    task.value.videoPath = ""
    task.value.subtasks = []

    const data = {
      project: formStore.project,
      performance: formStore.performance,
      aspectRatio: formStore.aspectRatio,
      prompt: formStore.prompt,
      negativePrompt: formStore.negativePrompt,
      checkpoint: formStore.checkpoint,
      loras: formStore.loras,
      motion: formStore.motion,
      cameraControl: formStore.cameraControl,
      highRes: formStore.highRes,
      fps: formStore.fps,
      duration: formStore.duration,
      seed: formStore.seed,
      promptBlocks: promptBlocks.map((x) => {
        return {
          start: x.start,
          prompt: x.prompt,
        }
      }),
    }
    try {
      const res = await submitTask(data)
      console.log("generate res", res.pipeline.pid)
      task.value.pid = res.pipeline.pid
      resume()
    } catch (e) {
      console.log("generate error", e)
      message.error(e.message)
      task.value.status = TStatus.ERROR
    }
  }

  return {
    task,
    isActive,
    modalVisible,
    submitExport,
    showModal,
    hideModal,
  }
})

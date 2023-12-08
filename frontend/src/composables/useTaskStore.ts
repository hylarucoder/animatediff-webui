export enum TStatus {
  PENDING = "PENDING",
  LOADING = "LOADING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

const status = ref(TStatus.SUCCESS)

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

export const useTaskStore = () => {
  return {
    status,
    progress,
  }
}

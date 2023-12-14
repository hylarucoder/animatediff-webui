<script lang="ts" setup>
import { formatProxyMedia, getTaskStatus, submitTask } from "~/client"
import { TStatus, useTaskStore } from "~/composables/useTaskStore"

const player = useTaskStore()
const videoPlayerStore = useVideoPlayer()

const optionsStore = useOptionsStore()
const { optPerformances } = optionsStore
const formStore = useFormStore()
const { sizeOpts, size, performance } = storeToRefs(formStore)

const timelineStore = useTimelineStore()
const { promptBlocks } = timelineStore
const emit = defineEmits<{
  (e: "closeModal"): void
}>()

const pullVideoPath = async () => {
  const res = await getTaskStatus()
  console.log(res)
  if (res?.progress?.main) {
    player.progress.value = res.progress
  }
  if (res.task?.status === "error") {
    player.status.value = TStatus.ERROR
  }
  if (!res?.task) {
    player.status.value = TStatus.ERROR
  }
  if (!res?.task?.videoPath) {
    return
  }
  player.status.value = TStatus.SUCCESS
  videoPlayerStore.loadVideo(formatProxyMedia(res.task.videoPath))
  // player.reloadVideo()
  clearInterval(pullInter)
}
let pullInter = null

const generate = async () => {
  player.status.value = TStatus.LOADING
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
    console.log("generate res", res)
    pullInter = setInterval(() => {
      pullVideoPath()
    }, 4000)
  } catch (e) {
    console.log("generate error", e)
    message.error(e.message)
    player.status.value = TStatus.ERROR
  }
}
</script>
<template>
  <a-modal
    centered
    :open="true"
    title="Export"
    ok-text="Export"
    @cancel="emit('closeModal')"
    @close="emit('closeModal')"
  >
    <div class="flex h-[400px] w-[500px] select-none">
      <div class="flex w-1/2 pr-5 pt-2">
        <div class="flex h-full w-full items-center justify-center bg-zinc-300">
          <div class="flex-col">
            <div>rendering</div>
            <div>time leps</div>
          </div>
        </div>
      </div>
      <div class="flex w-1/2">
        <a-form layout="vertical">
          <a-form-item label="Performance" required>
            <a-radio-group v-model:value="performance">
              <a-radio v-for="opt in optPerformances" :key="opt.value" :value="opt.value" :label="opt.label">
                {{ opt.label }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="Duration(s)" required>
            <a-input-number value="8" class="text-left" />
          </a-form-item>
          <a-form-item label="Output Size" required>
            <a-radio-group v-model:value="size">
              <a-radio v-for="opt in sizeOpts" :key="opt.value" :value="opt.value" :label="opt.label">
                {{ opt.label }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
        </a-form>
      </div>
    </div>
  </a-modal>
</template>

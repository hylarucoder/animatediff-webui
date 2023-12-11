<script setup lang="ts">
import { TStatus, useTaskStore } from "~/composables/useTaskStore"
import { formatProxyMedia, getTaskStatus, submitTask } from "~/client"

const timelineStore = useTimelineStore()
const { promptBlocks } = timelineStore

// const videoPlayerStore = useVideoPlayer()

const unpackStore = (store) => {
  return {
    state: storeToRefs(store),
    action: store,
  }
}

const formStore = useFormStore()
const {
  state: { preset, project },
  action: { loadPreset },
} = unpackStore(formStore)
const player = useTaskStore()
const optionsStore = useOptionsStore()
const { optPresets, optProjects, options } = optionsStore

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
  // videoPlayerStore.loadVideo(formatProxyMedia(res.task.videoPath))
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

const changePresets = (value: string) => {
  const _preset = options.presets.find((p) => p.name === value)
  if (!_preset) {
    return
  }
  loadPreset(_preset)
}
</script>

<template>
  <div class="flex h-[--header-height] w-full justify-evenly border-[1px] px-5 text-center">
    <div
      id="topbar"
      class="ant-form-item-no-mb form-item-no-feedback flex flex-1 items-center space-x-3 py-2 align-middle"
    >
      <AFormItem style="margin: 0" label="Preset">
        <ASelect
          :options="optPresets"
          :value="preset"
          show-search
          style="width: 200px"
          class="text-left"
          @update:value="changePresets"
        />
      </AFormItem>
      <AFormItem style="margin: 0" label="Project">
        <ASelect v-model:value="project" show-search :options="optProjects" style="width: 200px" class="text-left" />
      </AFormItem>
    </div>

    <div class="flex items-center justify-center space-x-3">
      <AButton :loading="player.status.value === TStatus.LOADING" @click="generate"> Export</AButton>
    </div>
  </div>
</template>

<style>
.ant-form-item-no-mb .ant-form-item {
  margin-bottom: 0 !important;
}
</style>

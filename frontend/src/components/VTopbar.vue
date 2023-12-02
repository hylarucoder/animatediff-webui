<script setup lang="ts">
import { TStatus } from "~/composables/usePlayer"
import { formatProxyMedia, getTaskStatus, submitTask } from "~/client"

const formStore = useFormStore()
const { preset, project, loadPreset } = formStore
const player = usePlayer()
const optionsStore = useOptionsStore()
const { optPresets, optProjects, options } = optionsStore

const pullVideoPath = async () => {
  const res = await getTaskStatus()
  console.log(res)
  if (res.progress.main) {
    player.progress.value = res.progress
  }
  if (!res.video_path) {
    return
  }
  player.video_url.value = formatProxyMedia(res.video_path)
  player.status.value = TStatus.SUCCESS
  player.reloadVideo()
  clearInterval(pull_inter)
}
let pull_inter = null

const generate = async () => {
  player.status.value = TStatus.LOADING
  const data = {
    project: formStore.project.value,
    performance: formStore.performance.value,
    aspect_ratio: formStore.aspect_ratio.value,
    prompt: formStore.prompt.value,
    negative_prompt: formStore.negative_prompt.value,
    checkpoint: formStore.checkpoint.value,
    loras: formStore.loras.value,
    motion: formStore.motion.value,
    motion_lora: formStore.motion_lora.value,
    fps: formStore.fps.value,
    duration: formStore.duration.value,
    seed: formStore.seed.value,
  }
  try {
    const res = await submitTask(data)
    console.log("generate res", res)
    pull_inter = setInterval(() => {
      pullVideoPath()
    }, 2000)
  } catch (e) {
    console.log("generate error", e)
    message.error(e.message)
    player.status.value = TStatus.ERROR
  }
}

const changePresets = (value: string) => {
  const _preset = options.value.presets.find((p) => p.name === value)
  if (!_preset) {
    return
  }
  loadPreset(_preset)
}
console.log("optPresets", toRaw(optPresets))
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
        <ASelect show-search v-model:value="project" :options="optProjects" style="width: 200px" class="text-left" />
      </AFormItem>
    </div>

    <div class="flex items-center justify-center space-x-3">
      <AButton :loading="player.status.value === TStatus.LOADING" @click="generate"> Generate</AButton>
      <!--      <AButton @click="pull_video_path">-->
      <!--        load video-->
      <!--      </AButton>-->
    </div>
  </div>
</template>

<style>
.ant-form-item-no-mb .ant-form-item {
  margin-bottom: 0 !important;
}
</style>

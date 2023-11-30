<script setup lang="ts">
import { urlPrefix } from "~/consts"
import { TStatus } from "~/composables/usePlayer"

const formStore = useFormStore()
const { preset, project } = formStore
const { loadPreset } = formStore
const player = usePlayer()
const optionsStore = useOptionsStore()
const { optPresets, optProjects, options } = optionsStore

const pull_video_path = () => {
  $fetch(urlPrefix + "/api/render/status", {
    method: "GET",
  }).then((res: any) => {
    if (!res.video_path) {
      return
    }
    player.video_url.value = urlPrefix + "/media?path=" + res.video_path
    player.status.value = TStatus.SUCCESS
    player.reloadVideo()
    clearInterval(pull_inter)
  })
}
let pull_inter = null

const generate = () => {
  player.status.value = TStatus.LOADING
  const data = {
    project: formStore.project.value,
    performance: formStore.performance.value,
    aspect_ratio: formStore.aspect_ratio.value,
    head_prompt: formStore.head_prompt.value,
    tail_prompt: formStore.tail_prompt.value,
    negative_prompt: formStore.negative_prompt.value,
    checkpoint: formStore.checkpoint.value,
    loras: formStore.loras.value,
    motion: formStore.motion.value,
    motion_lora: formStore.motion_lora.value,
    // fps: formStore.fps.value,
    // duration: formStore.duration.value,
    // seed: formStore.seed.value,
  }
  $fetch(urlPrefix + "/api/render/submit", {
    method: "POST",
    body: JSON.stringify(data),
  }).then((res) => {
    console.log(res)
    pull_inter = setInterval(() => {
      pull_video_path()
    }, 4000)
  })
}

const changePresets = (value: string) => {
  const preset = options.value.presets.find((p) => p.name === value)
  if (!preset) {
    return
  }
  loadPreset(preset)
}
console.log("optPresets", toRaw(optPresets))
</script>

<template>
  <div class="flex w-full justify-evenly border-[1px] px-5 text-center">
    <div
      id="topbar"
      class="ant-form-item-no-mb form-item-no-feedback flex flex-1 items-center space-x-3 py-2 align-middle"
    >
      <AFormItem style="margin: 0" label="Preset">
        <ASelect
          :options="optPresets"
          :model-value="preset"
          style="width: 200px"
          class="text-left"
          @update:value="changePresets"
        />
      </AFormItem>
      <AFormItem style="margin: 0" label="Project">
        <ASelect v-model:value="project" :options="optProjects" style="width: 200px" class="text-left" />
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
#topbar ant-form-item {
  margin-bottom: 0px !important;
}

.ant-form-item-no-mb .ant-form-item {
  margin-bottom: 0 !important;
}
</style>

<script setup lang="ts">
import { CashOutline } from "@vicons/ionicons5"
import { urlPrefix } from "~/consts"
import { TStatus } from "~/composables/usePlayer"

const { form, setPreset } = useAnimateForm()
const player = usePlayer()
const { options } = useStore()

const pull_video_path = () => {
  $fetch(
    urlPrefix + "/api/render/status",
    {
      method: "GET",
    },
  ).then((res: any) => {
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
    ...form,
    project: form.value.project,
  }
  $fetch(
    urlPrefix + "/api/render/submit",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  ).then((res) => {
    console.log(res)
    pull_inter = setInterval(() => {
      pull_video_path()
    }, 4000)
  })
}
const presetsOption = options.value.presets.map((preset) => {
  return {
    label: preset.name,
    value: preset.name,
  }
})
const projectsOption = options.value.projects.map((p) => {
  return {
    label: p,
    value: p,
  }
})

const changePresets = (value: string) => {
  console.log("value", value)
  const preset = options.value.presets.find((p) => p.name === value)
  if (!preset) {
    return
  }
  setPreset(preset)
}
console.log(presetsOption)

</script>

<template>
  <div class="w-full flex justify-evenly text-center px-5 border-[1px]">
    <div id="topbar" class="flex items-center flex-1 space-x-3 form-item-no-feedback align-middle py-2">
      <AFormItem
        style="margin-bottom: 10px !important;"
        label="Preset"
      >
        <ASelect
          :options="presetsOption"
          :model-value="form.preset"
          style="width: 200px;"
          class="text-left"
          @update:value="changePresets"
        />
      </AFormItem>
      <AFormItem
        style="margin: 0"
        label="Project"
      >
        <ASelect
          v-model:value="form.project"
          :options="projectsOption"
          style="width: 200px;"
          class="text-left"
        />
      </AFormItem>
    </div>

    <div class="space-x-3 flex justify-center items-center">
      <AButton :loading="player.status.value === TStatus.LOADING" @click="generate">
        Generate
      </AButton>
      <AButton @click="pull_video_path">
        load video
      </AButton>
    </div>
  </div>
</template>

<style>
#topbar ant-form-item {
  margin-bottom: 0px !important;
}

</style>

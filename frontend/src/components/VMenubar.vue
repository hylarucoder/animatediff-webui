<script setup lang="ts">
import { useVideoExportStore } from "~/composables/videoExport"

const formStore = useFormStore()
const { preset, project } = storeToRefs(formStore)
const { loadPreset } = formStore
const optionsStore = useOptionsStore()
const { optPresets, optProjects, options } = storeToRefs(optionsStore)
const videoExportStore = useVideoExportStore()
const { modalVisible } = storeToRefs(videoExportStore)

const changePresets = (value: string) => {
  const _preset = options.value.presets.find((p) => p.name === value)
  if (!_preset) {
    return
  }
  loadPreset(_preset)
}
console.log(optProjects, optPresets)
</script>

<template>
  <div class="relative flex h-[--header-height] w-full justify-between border-b-[1px] border-zinc-100 px-5">
    <div class="ant-form-item-no-mb form-item-no-feedback flex flex-1 items-center space-x-3 py-2 align-middle">
      <a-form-item style="margin: 0" label="Preset">
        <a-select
          :options="optPresets"
          :value="preset"
          show-search
          style="width: 200px"
          @update:value="changePresets"
        />
      </a-form-item>
      <a-form-item style="margin: 0" label="Project">
        <a-select v-model:value="project" show-search :options="optProjects" style="width: 200px" />
      </a-form-item>
    </div>

    <div class="flex items-center justify-center space-x-3">
      <v-modal-export v-if="modalVisible" @close-modal="videoExportStore.hideModal()" />
      <a-button @click="videoExportStore.showModal()"> Export</a-button>
    </div>
  </div>
</template>

<style>
.ant-form-item-no-mb .ant-form-item {
  margin-bottom: 0 !important;
}
</style>

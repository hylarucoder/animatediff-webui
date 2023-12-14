<script setup lang="ts">
const formStore = useFormStore()
const { preset, project } = storeToRefs(formStore)
const { loadPreset } = formStore
const optionsStore = useOptionsStore()
const { optPresets, optProjects, options } = optionsStore

const changePresets = (value: string) => {
  const _preset = options.presets.find((p) => p.name === value)
  if (!_preset) {
    return
  }
  loadPreset(_preset)
}
const modalExportVisible = ref(false)
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
      <v-modal-export v-if="modalExportVisible" @close-modal="modalExportVisible = false" />
      <a-button @click="modalExportVisible = true"> Export</a-button>
    </div>
  </div>
</template>

<style>
.ant-form-item-no-mb .ant-form-item {
  margin-bottom: 0 !important;
}
</style>

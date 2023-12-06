<script setup lang="ts">
const panelView = usePanelView()
const { projectSetting, controlnet, prompt } = storeToRefs(panelView)
</script>
<template>
  <div class="relative w-[400px] overflow-auto border-b-[1px] border-r-[1px] border-gray-200 px-5 py-2">
    <VProjectSettingPanel v-if="projectSetting" />
    <VPromptPanel v-if="prompt" class="absolute left-0 top-0 z-10 bg-white" />
    <VControlnetPanel v-if="controlnet" class="absolute left-0 top-0 z-20 bg-white" />
  </div>
</template>

<script setup lang="ts">
import { useActiveBlockStore } from "~/composables/block"

const panelView = usePanelView()
const activeBlockStore = useActiveBlockStore()
const { block: activeBlock } = storeToRefs(activeBlockStore)
const { projectSetting } = storeToRefs(panelView)
</script>
<template>
  <div class="relative w-[400px] overflow-auto border-b-[1px] border-r-[1px] border-zinc-100 px-5">
    <VProjectSettingPanel v-if="projectSetting" />
    <VPromptPanel v-if="activeBlock" class="absolute left-0 top-0 z-10 bg-white" />
  </div>
</template>

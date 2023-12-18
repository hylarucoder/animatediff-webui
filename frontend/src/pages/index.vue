<script setup lang="ts">
import { useOptionsStore } from "~/composables/options"
import { useActiveBlockStore } from "~/composables/block"

const optionsStore = useOptionsStore()
const { optionLoaded } = storeToRefs(optionsStore)
const activeBlock = useActiveBlockStore()
await optionsStore.init()

const cleanBlock = useThrottleFn(() => {
  console.log("Clicked outside of .timetrack-block and .timetrack-block-editor")
  activeBlock.deleteBlock()
}, 1000)

document.addEventListener("click", function (event) {
  const isClickInsideElement =
    event?.target?.closest(".timeline-track-block") || event?.target?.closest(".timeline-track-block-editor")

  if (!isClickInsideElement) {
    cleanBlock()
  }
})
</script>
<template>
  <a-spin v-if="!optionLoaded" />
  <div v-else class="h-screen w-full p-0 px-0">
    <VMenubar class="border-1" />
    <div class="border-x-1 border-b-1 flex h-[--workspace-height] justify-between">
      <VMainPlayer />
      <VRightSidebar />
    </div>
    <VTimelineWindow />
  </div>
</template>

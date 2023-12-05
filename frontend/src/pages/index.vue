<script setup lang="ts">
import { useOptionsStore } from "~/composables/options"

const optionsStore = useOptionsStore()
const { optionLoaded } = storeToRefs(optionsStore)
await optionsStore.init()
</script>
<template>
  <a-spin v-if="!optionLoaded" />
  <div v-else class="h-screen w-full p-0 px-0">
    <VMenubar class="border-1" />
    <div class="border-x-1 border-b-1 flex h-[--workspace-height] justify-between">
      <VMainPlayer />
      <VRightSidebar />
    </div>
    <VTimeline />
    <!--    <VStatusbar />-->
  </div>
</template>

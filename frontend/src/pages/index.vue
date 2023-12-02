<script setup lang="ts">
import { useOptionsStore } from "~/composable/store"

const optionsStore = useOptionsStore()
const { optionLoaded } = optionsStore
await optionsStore.init()
</script>
<template>
  <a-spin v-if="!optionLoaded" />
  <div v-else class="h-screen w-full p-0 px-0">
    <VTopbar class="border-1" />
    <div class="border-x-1 border-b-1 flex h-[--workspace-height] justify-between">
      <VMainPlayer />
      <VRightSidebar />
    </div>
    <VStatusbar />
  </div>
</template>

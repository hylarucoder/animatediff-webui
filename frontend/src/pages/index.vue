<script setup lang="ts">
const optionsStore = useOptionsStore()
const {
  optionLoaded,
} = storeToRefs(optionsStore)
await optionsStore.init()
</script>
<template>
  <a-spin v-if="!optionLoaded" />
  <div v-else class="w-full p-0 px-8">
    <VTopbar class="border-1" />
    <div class="flex justify-between border-x-1 border-b-1">
      <VMainPlayer/>
      <VRightSidebar/>
    </div>
  </div>
</template>


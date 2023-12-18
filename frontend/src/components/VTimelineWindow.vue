<script setup lang="ts">
const timeline = useTimelineStore()
onBeforeMount(() => {
  timeline.initBlocks()
})
</script>
<template>
  <div
    class="relative h-[--timeline-height] w-full overflow-scroll border-x-[1px] border-b-[1px] border-zinc-100 bg-zinc-50 p-0"
  >
    <!--  VTimeToolbar  -->
    <VTimelineToolbar />
    <div class="flex w-full">
      <!--  VTimelineTrackLeftPanel -->
      <VTimelineTrackLeftPanel />
      <!--  VTimelineTracks -->
      <VTimelineTracks />
    </div>
  </div>
</template>

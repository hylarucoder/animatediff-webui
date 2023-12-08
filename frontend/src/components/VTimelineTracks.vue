<script setup lang="ts">
const timelineStore = useTimelineStore()
const { refTimeline } = storeToRefs(timelineStore)
</script>
<template>
  <div ref="refTimeline" class="relative w-full">
    <VTimelineTracksHeader />

    <div class="relative w-full space-y-[1px]">
      <VTimelineTrack />
      <!--      <div v-for="timeline in optTimelines" class="flex h-[40px] rounded border-b-[1px] text-white">-->
      <!--        <VTimelineBlock-->
      <!--          :is-virtual="false"-->
      <!--          v-for="(block, key) in timeline.blocks"-->
      <!--          :key="key"-->
      <!--          :unit-width="unitWidth"-->
      <!--          :block="block"-->
      <!--        />-->
      <!--      </div>-->
    </div>
  </div>
</template>

<script setup lang="ts">
const timelineStore = useTimelineStore()
const { leftPanelWidth } = storeToRefs(timelineStore)
const optTimelines = [
  {
    title: "prompt",
  },
  // {
  //   title: "ip-adapter",
  // },
  // {
  //   title: "depth",
  // },
]
</script>
<template>
  <div
    class="h-full select-none border-b-[1px] border-r-[1px] border-zinc-200"
    :style="{
      width: leftPanelWidth + 'px',
    }"
  >
    <div class="flex h-[40px] rounded border-b-[1px] border-zinc-100 px-[8px] text-white" />
    <div
      v-for="timeline in optTimelines"
      class="flex h-[40px] rounded border-b-[1px] border-zinc-100 px-[8px] text-white"
    >
      <div class="flex w-[80px] overflow-ellipsis">
        <span class="line-clamp-1 block w-[80px] cursor-pointer text-center text-sm text-zinc-600">
          {{ timeline.title }}
        </span>
      </div>
    </div>
  </div>
</template>

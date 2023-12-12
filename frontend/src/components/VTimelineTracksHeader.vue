<script setup lang="ts">
const timelineStore = useTimelineStore()
const { duration, refRuler, unitWidth, fps, isMouseOutside, rulerPos } = storeToRefs(timelineStore)
const videoPlayerStore = useVideoPlayer()
const playAxis = usePlayAxis()
const { style, x: timeStartPx, el, isDragging } = storeToRefs(playAxis)

const seek = useThrottleFn(() => {
  videoPlayerStore.seek(timeStartPx.value / 200)
}, 500)
watch([timeStartPx, isDragging], (value) => {
  if (value[1]) {
    seek()
  }
})
</script>
<template>
  <div ref="el" :style="style" class="absolute z-[100] h-full w-px cursor-move bg-red-500">
    <svg
      class="absolute -left-[12px] -top-3 h-6 w-6 fill-current text-red-500"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 50 50"
    >
      <polygon points="25,40 0,10 50,10" fill="red" />
    </svg>
  </div>
  <div
    v-show="!isMouseOutside"
    :style="{ left: `${rulerPos}px` }"
    class="pointer-events-none absolute z-[90] h-full w-px bg-red-500"
  >
    <svg
      class="absolute -left-[12px] -top-3 h-6 w-8 fill-current text-gray-500"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 50 50"
    >
      <polygon points="25,40 0,10 50,10" fill="black" />
    </svg>
  </div>
  <div ref="refRuler" class="timeline relative h-[40px] select-none border-b-[1px]" @click.prevent="onClickRule">
    <div
      v-for="i in duration * fps"
      :key="i"
      class="absolute z-[100] w-[25px]"
      :style="{
        left: i * unitWidth + 'px',
        width: unitWidth + 'px',
      }"
    >
      <span
        v-if="i % fps"
        class="block select-none text-[10px] font-semibold text-gray-400"
        :style="{ width: unitWidth + 'px' }"
      >
        |
      </span>
      <span
        v-else
        class="text-ms block w-[25px] select-none font-semibold text-gray-600"
        :style="{ width: unitWidth + 'px' }"
      >
        {{ i / fps }}s
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
const timelineStore = useTimelineStore()
const { duration, refRuler, unitWidth, fps, isMouseOutside, rulerPos } = storeToRefs(timelineStore)
const videoPlayerStore = useVideoPlayer()
const playAxis = usePlayAxis()
const { style, x: timeStartPx, el } = storeToRefs(playAxis)

const seek = useThrottleFn(() => {
  videoPlayerStore.seek(timeStartPx.value / 200)
}, 500)
watch(timeStartPx, () => {
  seek()
})

const onClickAAA = () => {
  console.log("onClickAAA")
}
// `style` will be a helper computed for `left: ?px; top: ?px;`
</script>
<template>
  <div ref="el" :style="style" class="absolute z-[1000] h-full w-px cursor-move bg-red-500">
    <svg
      class="absolute -left-[12px] -top-3 h-6 w-6 fill-current text-red-500"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 50 50"
    >
      <path
        d="M25 3C14.4 3 6 11.4 6 22c0 7.4 5 13.7 12 16.6V47c0 1.7 1.3 3 3 3s3-1.3 3-3v-1h2v1c0 1.7 1.3 3 3 3s3-1.3 3-3V38.6c7-2.9 12-9.1 12-16.6 0-10.6-8.4-19-14-19z"
      />
    </svg>
  </div>
  <div
    v-show="!isMouseOutside"
    :style="{ left: `${rulerPos}px` }"
    class="absolute z-[900] h-full w-px bg-red-500"
    @click="onClickAAA"
  >
    <svg
      class="absolute -left-[12px] -top-3 h-6 w-6 fill-current text-gray-500"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 50 50"
    >
      <path
        d="M25 3C14.4 3 6 11.4 6 22c0 7.4 5 13.7 12 16.6V47c0 1.7 1.3 3 3 3s3-1.3 3-3v-1h2v1c0 1.7 1.3 3 3 3s3-1.3 3-3V38.6c7-2.9 12-9.1 12-16.6 0-10.6-8.4-19-14-19z"
      />
    </svg>
  </div>
  <div ref="refRuler" class="timeline relative h-[40px] select-none border-b-[1px]">
    <div
      v-for="i in duration * fps"
      :key="i"
      class="absolute z-[1000] w-[25px]"
      :style="{
        left: i * unitWidth + 'px',
        width: unitWidth + 'px',
      }"
    >
      <span v-if="i % fps" class="block text-[10px] font-semibold text-gray-400" :style="{ width: unitWidth + 'px' }">
        |
      </span>
      <span v-else class="text-ms block w-[25px] font-semibold text-gray-600" :style="{ width: unitWidth + 'px' }">
        {{ i / fps }}s
      </span>
    </div>
  </div>
</template>

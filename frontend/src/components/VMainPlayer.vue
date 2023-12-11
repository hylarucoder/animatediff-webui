<script setup lang="ts">
import { TStatus, useTaskStore } from "~/composables/useTaskStore"
import { formatProxyMedia } from "~/client"
import "video.js/dist/video-js.css"

const videoPlayerStore = useVideoPlayer()
const { videoRef, currentTime, waiting, playing, duration } = storeToRefs(videoPlayerStore)
const { loadVideo, play, pause } = videoPlayerStore
const { status } = useTaskStore()
onMounted(() => {
  const src = formatProxyMedia(
    "C:\\AIGC\\App\\animatediff-webui\\projects\\001-demo\\draft\\2023-12-07T13-52-47\\video.mp4",
  )
  loadVideo(src)
})

const formatDurationHHMMSS = (t: number) => {
  const hours = Math.floor(t / 3600)
  const minutes = Math.floor((t - hours * 3600) / 60)
  const seconds = Math.floor(t - hours * 3600 - minutes * 60)
  const hoursStr = hours.toString().padStart(2, "0")
  const minutesStr = minutes.toString().padStart(2, "0")
  const secondsStr = seconds.toString().padStart(2, "0")
  return `${hoursStr}:${minutesStr}:${secondsStr}`
}
</script>
<template>
  <div class="w-full overflow-auto border-x-[1px] border-b-[1px] border-gray-200 p-2 px-5">
    <div v-show="status !== TStatus.SUCCESS" class="flex h-full min-h-[400px] w-full items-center justify-center">
      <div v-show="status === TStatus.PENDING" class="text-center">click generate</div>
      <div v-show="status === TStatus.ERROR" class="text-center">error</div>
      <a-spin v-show="status === TStatus.LOADING" class="w-full text-center"> generating video </a-spin>
    </div>
    <div v-show="status === TStatus.SUCCESS" class="flex h-full min-h-[400px] w-full flex-col">
      <video ref="videoRef" crossorigin="anonymous" class="h-[600px] w-full" controls />
      <!--      <div v-if="waiting" class="pointer-events-none absolute inset-0 grid place-items-center bg-black bg-opacity-20">-->
      <!--        <a-spin />-->
      <!--      </div>-->
      <!--      <div class="flex flex-row items-center">-->
      <!--        <a-button v-if="!playing" @click.prevent="play">-->
      <!--          <span class="i-mdi-play" />-->
      <!--        </a-button>-->
      <!--        <a-button v-if="playing" @click.prevent="pause">-->
      <!--          <span class="i-mdi-pause" />-->
      <!--        </a-button>-->
      <!--        <a-button>-->
      <!--          <span class="i-mdi-volume" />-->
      <!--        </a-button>-->
      <!--        <div-->
      <!--          class="relative ml-2 h-2 w-32 cursor-pointer select-none rounded bg-black bg-opacity-20 dark:bg-white dark:bg-opacity-10"-->
      <!--        >-->
      <!--          <div class="relative h-full w-full overflow-hidden rounded">-->
      <!--            <div-->
      <!--              class="absolute left-0 top-0 h-full w-full rounded bg-emerald-700 opacity-30"-->
      <!--              style="transform: translateX(-100%)"-->
      <!--            />-->
      <!--            <div class="relative h-full w-full rounded bg-emerald-500" style="transform: translateX(0%)" />-->
      <!--          </div>-->
      <!--          <div class="absolute inset-0 opacity-0 hover:opacity-100">&lt;!&ndash;[&ndash;&gt;&lt;!&ndash;]&ndash;&gt;</div>-->
      <!--        </div>-->
      <!--        <div class="ml-2 flex flex-1 flex-col text-sm">-->
      <!--          {{ formatDurationHHMMSS(currentTime) }}-->
      <!--          /-->
      <!--          {{ formatDurationHHMMSS(duration) }}-->
      <!--        </div>-->
      <!--        <div class="relative mr-2">-->
      <!--          <a-button>-->
      <!--            <span class="i-mdi-volume" />-->
      <!--            4:3-->
      <!--          </a-button>-->
      <!--        </div>-->
      <!--      </div>-->
    </div>
  </div>
</template>

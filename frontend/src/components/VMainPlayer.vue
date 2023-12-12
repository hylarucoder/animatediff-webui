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
const activeKey = ref("1")
</script>
<template>
  <div class="w-full overflow-auto border-x-[1px] border-b-[1px] border-gray-200 p-2 px-5">
    <a-tabs v-model:activeKey="activeKey" class="relative z-10">
      <a-tab-pane key="1" tab="Player" class="">
        <div v-show="status !== TStatus.SUCCESS" class="flex h-full min-h-[400px] w-full items-center justify-center">
          <div v-show="status === TStatus.PENDING" class="text-center">click generate</div>
          <div v-show="status === TStatus.ERROR" class="text-center">error</div>
          <a-spin v-show="status === TStatus.LOADING" class="w-full text-center"> generating video</a-spin>
        </div>
        <div v-show="status === TStatus.SUCCESS" class="flex h-full min-h-[400px] w-full flex-col">
          <video ref="videoRef" crossorigin="anonymous" class="h-[600px] w-full" controls />
        </div>
      </a-tab-pane>
      <a-tab-pane key="2" tab="Media" class="">
        <v-finder
          id="media-finder"
          adapter="local"
          class="z-1100 h-[600px] w-full bg-white"
          url="http://localhost:8000/api/finder"
        />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

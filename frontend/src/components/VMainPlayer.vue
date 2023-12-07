<script setup lang="ts">
import { TStatus, usePlayer } from "~/composables/usePlayer"
import { formatProxyMedia } from "~/client"

const videoPlayerStore = useVideoPlayer()
const { videoRef } = storeToRefs(videoPlayerStore)
const { loadVideo } = videoPlayerStore

const { status } = usePlayer()
onMounted(() => {
  const src = formatProxyMedia(
    "C:\\AIGC\\App\\animatediff-webui\\projects\\001-demo\\draft\\2023-12-07T13-52-47\\video.mp4",
  )
  loadVideo(src)
})
</script>
<template>
  <div class="w-full overflow-auto border-x-[1px] border-b-[1px] border-gray-200 p-2 px-5">
    <div class="flex h-full min-h-[400px] w-full items-center justify-center" v-show="status !== TStatus.SUCCESS">
      <div v-show="status === TStatus.PENDING" class="text-center">click generate</div>
      <div v-show="status === TStatus.ERROR" class="text-center">error</div>
      <a-spin v-show="status === TStatus.LOADING" class="w-full text-center">generating video</a-spin>
    </div>
    <div v-show="status === TStatus.SUCCESS" class="flex h-full min-h-[400px] w-full">
      <video ref="videoRef" class="h-[600px] w-full" controls />
    </div>
  </div>
</template>

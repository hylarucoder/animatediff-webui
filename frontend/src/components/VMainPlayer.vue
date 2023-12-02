<script setup lang="ts">
import { TStatus, usePlayer } from "~/composable/usePlayer"

const { progress, status, video_url, videoRef } = usePlayer()

watch(
  () => video_url,
  (newUrl, oldUrl) => {
    videoRef?.value?.load()
  },
)
</script>
<template>
  <div class="w-full overflow-auto border-x-[1px] border-b-[1px] border-gray-200 p-2 px-5">
    <a-tabs type="line" animated>
      <a-tab-pane key="preview" tab="Preview">
        <div class="flex h-full min-h-[400px] w-full items-center justify-center" v-show="status !== TStatus.SUCCESS">
          <div v-show="status === TStatus.PENDING" class="text-center">click generate</div>
          <div v-show="status === TStatus.ERROR" class="text-center">error</div>
          <a-spin v-show="status === TStatus.LOADING" class="w-full text-center">generating video</a-spin>
        </div>
        <div v-show="status === TStatus.SUCCESS" class="flex h-full min-h-[400px] w-full">
          <video ref="videoRef" class="h-[600px] w-full" controls>
            <source :src="video_url" type="video/mp4">
          </video>
        </div>
      </a-tab-pane>
      <a-tab-pane key="image_prompt" tab="Image Prompt">
        <div class="h-full w-full">image_prompt</div>
      </a-tab-pane>
      <a-tab-pane key="controlnet" tab="Controlnet">
        <div class="h-full w-full">Controlnet</div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

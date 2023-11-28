<script setup lang="ts">
import { TStatus } from "~/composables/usePlayer"

const {
  status,
  video_url,
  videoRef,
} = usePlayer()

watch(() => video_url, (newUrl, oldUrl) => {
  console.log("watch")
  videoRef?.value?.load()
})
</script>
<template>
  <div class="min-w-[800px] max-h-[800px] overflow-auto w-full border-gray-200 border-x-[1px] border-b-[1px] p-2 px-5">
    <a-tabs type="line" animated>
      <a-tab-pane key="preview" tab="Preview">
        <div class="h-full w-full">
          <div v-show="status === TStatus.PENDING" class="text-center">
            click generate
          </div>
          <div v-show="status === TStatus.ERROR" class="text-center">
            error
          </div>
          <div v-show="status === TStatus.LOADING" class="text-center">
            loading
          </div>
          <video
              v-show="status === TStatus.SUCCESS"
              ref="videoRef"
              class="w-full max-h-[700px]"
              controls
          >
            <source :src="video_url" type="video/mp4">
          </video>
        </div>
      </a-tab-pane>
      <a-tab-pane key="image_prompt" tab="Image Prompt">
        <div class="h-full w-full">
          image_prompt
        </div>
      </a-tab-pane>
      <a-tab-pane key="controlnet" tab="Controlnet">
        <div class="h-full w-full">
          Controlnet
        </div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

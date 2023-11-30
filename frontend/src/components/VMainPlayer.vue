<script setup lang="ts">
import { TStatus } from "~/composables/usePlayer"

const { tasks, status, video_url, videoRef } = usePlayer()

watch(
  () => video_url,
  (newUrl, oldUrl) => {
    console.log("watch")
    videoRef?.value?.load()
  },
)
// computed not finished tasks
const notCompletedTasks = computed(() => {
  return tasks.value.filter((task) => task.completed < 100)
})
</script>
<template>
  <div class="max-h-[800px] w-full min-w-[800px] overflow-auto border-x-[1px] border-b-[1px] border-gray-200 p-2 px-5">
    <a-tabs type="line" animated>
      <a-tab-pane key="preview" tab="Preview">
        <div class="flex h-full min-h-[400px] w-full items-center justify-center">
          <div v-show="status === TStatus.PENDING" class="text-center">click generate</div>
          <div v-show="status === TStatus.ERROR" class="text-center">error</div>
          <a-spin v-show="status === TStatus.LOADING" class="w-full text-center">generating video</a-spin>
          <video v-show="status === TStatus.SUCCESS" ref="videoRef" class="max-h-[700px] w-full" controls>
            <source :src="video_url" type="video/mp4" />
          </video>
        </div>
        <div class="h-[150px] overflow-auto">
          <div v-for="task in notCompletedTasks" :key="task.description">
            <span>{{ task.description }}</span>
            <a-progress :percent="task.completed" />
          </div>
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

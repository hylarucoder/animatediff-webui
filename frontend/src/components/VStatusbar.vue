<script lang="ts" setup>
const { progress, status, video_url, videoRef } = usePlayer()
// computed not finished tasks
const notCompletedTasks = computed(() => {
  console.log("cp", toRaw(progress))
  return (progress.tasks || []).filter((task) => task.completed < 100)
})
</script>
<template>
  <div class="h-[30px] overflow-hidden border-x-[1px] border-b-[1px] px-2">
    <div class="max-w-[500px]">
      <div class="h-[150px]">
        <span>{{ progress.main?.description }}</span>
        <a-progress :percent="progress.main?.completed" />
      </div>
      <div class="h-[150px]">
        <div v-for="task in notCompletedTasks" :key="task.description">
          <span>{{ task.description }}</span>
          <a-progress :percent="task.completed" />
        </div>
      </div>
    </div>
  </div>
</template>

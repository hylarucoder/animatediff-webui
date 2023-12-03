<script lang="ts" setup>
import { usePlayer } from "~/composables/usePlayer"

const { progress } = usePlayer()
// computed not finished tasks
const notCompletedTasks = computed(() => {
  console.log("cp", toRaw(progress))
  // return (progress.value.tasks || []).filter((task) => task.completed < 100)
  return progress.value.tasks.filter((task) => task.completed < 100)
})
</script>
<template>
  <div class="h-[30px] overflow-hidden border-x-[1px] border-b-[1px] px-2">
    <a-popover class="w-[400px] overflow-y-scroll">
      <template #content>
        <div class="h-[150px] w-[400px]">
          <div v-for="task in notCompletedTasks" :key="task.description">
            <span>{{ task.description }}</span>
            <a-progress :percent="task.completed" />
          </div>
        </div>
      </template>
      <div class="flex h-[30px]">
        <span>{{ progress.main.description }}</span>
        <a-progress :percent="progress.main.completed" />
      </div>
    </a-popover>
  </div>
</template>

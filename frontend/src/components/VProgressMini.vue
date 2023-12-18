<script lang="ts" setup>
const props = defineProps({
  description: {
    type: String,
    required: true,
  },
  completed: {
    type: Number,
    required: true,
  },
})

const status = computed(() => {
  return props.completed >= 100 ? "success" : "active"
})
</script>
<template>
  <div class="flex flex-col py-0 font-mono">
    <span class="my-0 line-clamp-1 w-[150px] text-[10px]">
      {{ description }}
    </span>
    <a-progress class="pgr-sm" :show-info="false" :stroke-width="4" :percent="completed" :status="status" />
  </div>
</template>

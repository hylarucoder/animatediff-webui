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
  <div class="flex w-[200px] items-center text-left">
    <span class="line-clamp-1 text-[10px]">
      {{ description }}
    </span>
  </div>
  <a-progress class="pgr-sm" :show-info="false" :stroke-width="4" :percent="completed" :status="status" />
</template>

<template>
  <div class="flex w-1/2">
    <template v-if="layout === 'left'">
      <div class="mr-2 flex items-center justify-center">
        <span :class="icon" class="h-5 w-5 text-sm leading-6 text-zinc-600" />
      </div>
      <slot />
    </template>
    <template v-else>
      <slot />
      <div class="ml-2 flex items-center justify-center">
        <span :class="icon" class="h-5 w-5 text-sm leading-6 text-zinc-600" />
      </div>
    </template>
  </div>
</template>
<script lang="ts" setup>
defineProps<{
  icon: string
  layout: "left" | "right"
}>()
</script>

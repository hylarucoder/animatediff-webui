<template>
  <div class="flex">
    <h3
      id="modal-title"
      class="mb-2 text-lg font-medium leading-6 text-gray-900 dark:text-gray-400"
      :aria-label="selection.item.path"
      data-microtip-position="bottom-right"
      role="tooltip"
    >
      {{ selection.item.basename }}
    </h3>
  </div>
  <div></div>
</template>

<script setup lang="ts">
const emit = defineEmits(["load"])

defineProps({
  selection: Object,
})

onMounted(() => {
  emit("load")
})
</script>

<template>
  <div
    class="grid-rows-auto grid gap-5"
    :class="{
      'grid-cols-4': images.length % 4 === 0,
      'grid-cols-3': images.length % 3 === 0,
      'grid-cols-2': images.length % 2 === 0,
      'grid-cols-1': images.length % 1 === 0,
    }"
  >
    <v-gallery-item v-for="(item, index) in images" :key="index" :aspect="aspect" :src="item" />
  </div>
</template>

<script setup lang="ts">
defineProps({
  images: {
    type: Array,
    required: true,
    default: () => [],
  },
  aspect: {
    type: String,
    default: "9:16",
    required: false,
  },
})
</script>

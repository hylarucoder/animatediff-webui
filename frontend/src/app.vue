<script setup lang="ts">
import { siteConfig } from "~/config/site"

useHead({
  title: siteConfig.title,
  script: [],
})

onMounted(() => {})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

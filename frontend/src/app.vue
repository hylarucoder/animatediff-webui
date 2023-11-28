<script setup lang="ts">
import {siteConfig} from "~/config/site"


useHead({
  title: siteConfig.title,
  script: [],
})

onMounted(() => {
})
</script>

<template>
  <NuxtLayout>
    <naive-config>
      <NuxtPage/>
    </naive-config>
  </NuxtLayout>
</template>

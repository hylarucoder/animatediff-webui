<template>
  <nuxt-img
    format="jpg"
    width="600"
    quality="90"
    sizes="600px sm:50vw"
    placeholder
    loading="lazy"
    v-bind="$attrs"
  />
</template>
<script setup lang="ts"></script>

<script setup lang="ts">
const activeKey = ref("1")
</script>
<template>
  <div class="w-full overflow-auto border-x-[1px] border-b-[1px] border-zinc-100">
    <a-tabs v-model:activeKey="activeKey" class="tab-main relative z-10">
      <a-tab-pane key="1" tab="Player" class="relative h-full w-full">
        <v-player />
      </a-tab-pane>
      <a-tab-pane key="2" tab="Media" class="">
        <v-finder
          id="media-finder"
          adapter="local"
          class="z-1100 h-[600px] w-full bg-white"
          url="http://localhost:8000/api/finder"
        />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

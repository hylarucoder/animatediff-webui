<script lang="ts" setup></script>
<template>
  <div class="flex h-[--timeline-toolbar-height] items-center border-b-[1px] border-zinc-200 px-2 pb-2 pt-2">
    <a-popover placement="topLeft">
      <template #content>
        <VTimelineLayoutPopover />
      </template>
      <div class="flex items-center">
        <span class="i-lucide-layout h-4 w-4 text-zinc-600" />
      </div>
    </a-popover>
  </div>
</template>

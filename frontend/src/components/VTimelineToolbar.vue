<script lang="ts" setup></script>
<template>
  <div class="flex items-center rounded-t px-2 pb-2 pt-2 shadow">
    <a-popover placement="topLeft">
      <template #content>
        <VTimelineLayoutPopover />
      </template>
      <div class="flex items-center">
        <LayoutOutlined />
      </div>
    </a-popover>
  </div>
</template>

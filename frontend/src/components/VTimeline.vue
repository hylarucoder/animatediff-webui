<script setup lang="ts">
const { timelines, duration, unitWidth, fps, promptLayer } = useTimeline()

const handleDragStart = (event) => {
  // Your drag start logic
}
const open = ref<boolean>(false)

const showDrawer = () => {
  open.value = true
}
const onClose = () => {
  open.value = false
}
const openPanel = () => {
  // TODO: 如果点到了其他地方, 则换掉
  // panelView.prompt.value = true
  // panelView.controlnet.value = false
}

const openControlnet = () => {
  // TODO: 如果点到了其他地方, 则换掉
  // panelView.prompt.value = false
  // panelView.controlnet.value = true
}
</script>
<template>
  <div class="relative h-[--timeline-height] w-full overflow-scroll border-x-[1px] border-b-[1px] border-gray-200">
    <div class="h-[--timeline-height] w-full bg-zinc-300 py-4 pl-4">
      <div class="flex">
        <a-popover placement="topLeft">
          <template #content>
            <VTimelineLayout />
          </template>
          <LayoutOutlined />
        </a-popover>
      </div>
      <div class="flex">
        <div class="w-[80px] px-[8px]">
          <span class="block w-[80px]"> timeline </span>
        </div>
        <div class="flex">
          <div
            v-for="i in duration * fps"
            class="absolute"
            :style="{
              marginLeft: i * unitWidth + 'px',
              width: unitWidth + 'px',
            }"
            :key="i"
          >
            <span v-if="i % fps" class="block text-sm text-gray-600" :style="{ width: unitWidth + 'px' }"> | </span>
            <span v-else class="block font-semibold text-gray-900" :style="{ width: unitWidth + 'px' }">
              {{ i / fps }}s
            </span>
          </div>
        </div>
      </div>

      <div class="absolute w-full space-y-[1px]">
        <div class="flex h-[40px] rounded bg-zinc-500 px-[8px] text-white">
          <div class="flex w-[80px] overflow-ellipsis" @click="showDrawer">
            <span class="line-clamp-1 block w-[80px] cursor-pointer text-sm">
              {{ promptLayer.title }}
            </span>
          </div>

          <div class="flex bg-zinc-500">
            <div
              v-for="(value, key) in promptLayer.blocks"
              :key="key"
              class="absolute m-0 h-[40px] items-center justify-center p-0 text-center"
              :style="{
                width: unitWidth + 'px',
                marginLeft: (value[0] / 125) * unitWidth + 'px',
              }"
              draggable="true"
              @dragstart="handleDragStart"
              @click="openPanel"
            >
              <div
                class="mx-[1px] h-full bg-amber-300 text-xs"
                :style="{
                  height: 'calc(100% - 4px)',
                  width: 'calc(100% - 4px)',
                }"
              >
                {{ value[0] / 1000 }}
              </div>
            </div>
          </div>
        </div>
        <div v-for="timeline in timelines" class="flex h-[40px] rounded bg-zinc-500 px-[8px] text-white">
          <div class="flex w-[80px] overflow-ellipsis">
            <span class="line-clamp-1 block w-[80px] text-sm">
              {{ timeline.title }}
            </span>
          </div>

          <div class="flex bg-zinc-500">
            <div
              v-for="(value, key) in timeline.blocks"
              :key="key"
              class="absolute m-0 items-center justify-center p-0 text-center"
              :style="{
                width: unitWidth + 'px',
                marginLeft: (value[0] / 125) * unitWidth + 'px',
              }"
              draggable="true"
              @dragstart="handleDragStart"
              @click="openControlnet"
            >
              <div
                class="mx-[1px] h-full bg-amber-300 text-xs"
                :style="{
                  height: 'calc(100% - 4px)',
                  width: 'calc(100% - 4px)',
                }"
              >
                {{ value[0] / 1000 }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

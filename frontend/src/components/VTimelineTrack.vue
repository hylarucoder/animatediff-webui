<script setup lang="ts">
import { useActiveBlockStore, useVirtualBlockStore } from "~/composables/block"
import type { TTrackBlock } from "~/composables/timeline"

const timelineStore = useTimelineStore()
const { unitWidth, promptBlocks } = storeToRefs(timelineStore)
const activeBlockStore = useActiveBlockStore()
const { block: activeBlock } = storeToRefs(activeBlockStore)

const virtualBlockStore = useVirtualBlockStore()
const { block: virtualBlock } = storeToRefs(virtualBlockStore)

const { addPromptBlocks, hasPromptBlocks, removePromptBlocks } = timelineStore

const refTimelineTrack = ref(null)

const getAlignedStart = (x: number) => {
  // 时间 1s 1000 毫秒
  // 距离 200px = fps * unitWith
  // return x * 5
  return Math.floor(Math.floor(x / 25) * 25) * 5
}

const updateVirtualBlock = (x) => {
  const start = getAlignedStart(x)
  if (x <= 0) {
    virtualBlockStore.deleteBlock()
    return
  }
  if (hasPromptBlocks(start)) {
    virtualBlockStore.deleteBlock()
    return
  }
  virtualBlockStore.activeBlock({
    start,
    duration: 125,
    prompt: "",
  })
}

const { elementX, isOutside } = useMouseInElement(refTimelineTrack)
watch([elementX, isOutside], ([elementX, isOutside]) => {
  if (!isOutside) {
    updateVirtualBlock(elementX)
  } else {
    virtualBlockStore.deleteBlock()
  }
})
const confirmVirtualBlock = (event) => {
  const start = getAlignedStart(elementX.value)
  addPromptBlocks({
    start,
    duration: 125,
    prompt: "",
  })
  virtualBlockStore.deleteBlock()
}
onKeyStroke("Backspace", (e) => {
  if (!activeBlock.value) {
    return
  }
  if (activeBlockStore.checkFocused()) {
    return
  }
  if (activeBlock.value.start) {
    removePromptBlocks(activeBlock.value.start)
    activeBlockStore.deleteBlock()
  }
  console.log("Key Delete pressed")
})
const onBlockSelect = (block: TTrackBlock) => {
  activeBlockStore.activeBlock(block)
}
const onDragStart = (e) => {
  console.log("drag start")
}
const onDragEnd = (e) => {
  console.log("drag end", e)
}
</script>
<template>
  <div ref="refTimelineTrack" class="relative flex h-[40px] rounded border-b-[1px] text-white">
    <VTimelineBlock
      v-for="(block, key) in promptBlocks"
      :key="key"
      :is-virtual="false"
      :unit-width="unitWidth"
      :block="block"
      @block-select="onBlockSelect"
      @drag-start="onDragStart"
      @drag-end="onDragEnd"
    />
    <VTimelineBlock
      v-if="virtualBlock"
      :is-virtual="true"
      :unit-width="unitWidth"
      :block="virtualBlock"
      @click.prevent="confirmVirtualBlock"
    />
  </div>
</template>

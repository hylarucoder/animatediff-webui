<script setup lang="ts">
const timelineStore = useTimeline()
const { unitWidth, fps, promptBlocks } = storeToRefs(timelineStore)

const { addPromptBlocks, hasPromptBlocks, removePromptBlocks } = timelineStore

const virtualBlock = ref(null)
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
    virtualBlock.value = null
    return
  }
  if (hasPromptBlocks(start)) {
    virtualBlock.value = null
    return
  }
  virtualBlock.value = {
    start,
    duration: 125,
    prompt: "",
  }
}

const { elementX, isOutside } = useMouseInElement(refTimelineTrack)
watch([elementX, isOutside], ([elementX, isOutside]) => {
  if (!isOutside) {
    updateVirtualBlock(elementX)
  } else {
    virtualBlock.value = null
  }
})
const confirmVirtualBlock = (event) => {
  const start = getAlignedStart(elementX.value)
  addPromptBlocks({
    start,
    duration: 125,
    prompt: "",
  })
  virtualBlock.value = null
}
const selectedBlock = ref(null)
onKeyStroke("Backspace", (e) => {
  if (selectedBlock.value) {
    removePromptBlocks(selectedBlock.value)
  }
  console.log("Key Delete pressed")
})
const onBlockSelect = (e) => {
  selectedBlock.value = e
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
      @click="confirmVirtualBlock"
    />
  </div>
</template>

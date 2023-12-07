<script lang="ts" setup>
import type { TTrackBlock } from "~/composables/timeline"

const props = defineProps<{
  block: TTrackBlock
  isVirtual: Boolean
}>()
const emit = defineEmits<{
  (e: "blockSelect", block: TTrackBlock): void
  (e: "dragStart", value: number): void
  (e: "dragEnd", value: number): void
}>()

const left = computed(() => {
  return Math.floor(props.block.start / 5)
})
const blockWidth = computed(() => {
  return 25
})

const refBlock = ref(null)
const selected = ref(false)
onClickOutside(refBlock, (event) => {
  selected.value = false
})

const onClickBlock = (block: TTrackBlock) => {
  selected.value = true
  emit("blockSelect", block)
}
</script>
<template>
  <div
    ref="refBlock"
    class="timeline-track-block absolute m-0 flex h-[40px] items-center justify-center p-0 text-center"
    :class="{
      'border-2 border-white ': selected && !isVirtual,
    }"
    :style="{
      width: blockWidth + 'px',
      left: left + 'px',
    }"
    draggable="true"
    @dragstart="emit('dragStart', block.start)"
    @dragend="emit('dragEnd', block.start)"
    @click.prevent="onClickBlock(block)"
  >
    <div
      class="mx-[1px] h-full text-xs"
      :class="{
        'bg-amber-500': !isVirtual,
        'bg-amber-300': isVirtual,
      }"
      :style="{
        height: 'calc(100% - 4px)',
        width: 'calc(100% - 4px)',
      }"
    >
      T
    </div>
  </div>
</template>

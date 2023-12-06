<script lang="ts" setup>
import type { TTrackBlock } from "~/composables/timeline"

const panelView = usePanelView()
// TODO: type: prompt, controlnet openpose .... , ip-adapater
const props = defineProps<{
  block: TTrackBlock
  isVirtual: Boolean
}>()
const emit = defineEmits<{
  (e: "blockSelect", value: number): void
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
// 定义点击打开面板的处理函数
const openPanel = () => {
  selected.value = true
  console.log("panelView", panelView.prompt)
  panelView.showPromptPanel()
  emit("blockSelect", props.block.start)
}
</script>
<template>
  <div
    ref="refBlock"
    class="absolute m-0 flex h-[40px] items-center justify-center p-0 text-center"
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
    @click="openPanel"
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
      {{ block.start }}
    </div>
  </div>
</template>

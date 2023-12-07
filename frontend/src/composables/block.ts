import type { TTrackBlock } from "~/composables/timeline"

export const useActiveBlockStore = defineStore("activeBlock", () => {
  const block = ref<TTrackBlock | null>(null)
  const refInput = ref(null)
  const activeBlock = (_block: TTrackBlock) => {
    block.value = _block
  }
  const blur = (_block: TTrackBlock) => {
    refInput.value?.blur()
  }
  const deleteBlock = () => {
    block.value = null
  }
  const checkFocused = () => {
    console.log(document.activeElement, refInput.value)
    return document.activeElement === refInput.value
  }
  return {
    refInput,
    checkFocused,
    block,
    blur,
    activeBlock,
    deleteBlock,
  }
})

export const useVirtualBlockStore = defineStore("virtualBlock", () => {
  const block = ref<TTrackBlock | null>(null)
  const start = ref(0)
  const prompt = ref("")
  const activeBlock = (_block: TTrackBlock) => {
    block.value = _block
  }
  const deleteBlock = () => {
    block.value = null
  }
  return {
    block,
    prompt,
    start,
    activeBlock,
    deleteBlock,
  }
})

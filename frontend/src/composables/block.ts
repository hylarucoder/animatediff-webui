import type { TTrackBlock } from "~/composables/timeline"

export const useActiveBlockStore = defineStore("activeBlock", () => {
  const block = ref<TTrackBlock | null>(null)
  const focused = ref(false)
  const refInput = ref(null)
  const activeBlock = (_block: TTrackBlock) => {
    block.value = _block
  }
  const blur = (_block: TTrackBlock) => {
    refInput.value?.blur()
  }
  const onFocus = () => {
    focused.value = true
  }

  const onBlur = () => {
    focused.value = false
  }
  const deleteBlock = () => {
    block.value = null
  }
  const checkFocused = () => {
    console.log("checkfocus", document.activeElement, refInput.value)
    return document.activeElement === refInput.value
  }
  return {
    refInput,
    onFocus,
    onBlur,
    checkFocused,
    block,
    focused,
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

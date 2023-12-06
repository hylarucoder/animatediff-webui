export const usePanelView = defineStore("panelView", () => {
  const projectSetting = ref(true)
  const prompt = ref(false)
  const controlnet = ref(false)
  const showPromptPanel = () => {
    prompt.value = true
  }
  return {
    projectSetting,
    prompt,
    controlnet,
    showPromptPanel,
  }
})

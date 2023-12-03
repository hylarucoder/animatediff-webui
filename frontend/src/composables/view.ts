export const usePanelView = defineStore("panelView", () => {
  const projectSetting = ref(true)
  const prompt = ref(false)
  const controlnet = ref(false)
  return {
    projectSetting,
    prompt,
    controlnet,
  }
})

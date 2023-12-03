const projectSetting = ref(true)
const prompt = ref(false)
const controlnet = ref(false)
export const usePanelView = () => {
  return {
    projectSetting,
    prompt,
    controlnet,
  }
}

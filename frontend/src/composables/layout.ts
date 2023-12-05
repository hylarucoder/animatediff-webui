export const useWindowLayoutStore = defineStore("windowLayout", () => {
  const windowWidth = "90vw"
  const windowHeight = "90vw"
  const topMenuHeight = 60
  const topTimelineHeight = 300
  return {
    windowHeight,
    windowWidth,
    topMenuHeight,
    topTimelineHeight,
  }
})

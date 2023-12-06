import { defineStore } from "pinia"
import { useMediaControls } from "@vueuse/core"

export const useVideoPlayer = defineStore("video", () => {
  // we won't expose this element directly
  const videoRef = ref<HTMLVideoElement>()
  const src = ref("")
  const { playing, volume, currentTime, togglePictureInPicture } = useMediaControls(videoRef, {
    src
  })

  function loadVideo(_src: string) {
    src.value = _src
    videoRef.value?.load()
  }

  return {
    videoRef,
    src,
    playing,
    volume,
    currentTime,
    loadVideo,
    togglePictureInPicture,
  }
})

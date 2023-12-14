import { defineStore } from "pinia"
import { useMediaControls } from "@vueuse/core"

export const usePlayAxis = defineStore("playAxis", () => {
  const el = ref<HTMLElement | null>(null)
  const { x, isDragging, style } = useDraggable(el, {
    initialValue: {
      x: 0,
    },
    axis: "x",
    containerElement: () => el.value?.parentElement,
  })

  return {
    el,
    x,
    isDragging,
    style,
  }
})

export const useVideoPlayer = defineStore("video", () => {
  // we won't expose this element directly
  const playAxis = usePlayAxis()
  const { x } = storeToRefs(playAxis)
  const videoRef = ref<HTMLVideoElement>()
  const src = ref("")
  const { playing, waiting, duration, seeking, volume, currentTime, togglePictureInPicture } = useMediaControls(
    videoRef,
    {
      src,
    },
  )
  const { isFullscreen, enter, exit, toggle } = useFullscreen(videoRef)

  watch([currentTime, playing], (value, oldValue) => {
    if (value[1] && !oldValue[1]) {
      // onStartPlay()
      console.log("---->", value, oldValue)
    }
    if (!value[1] && oldValue[1]) {
      // onStopPlay()
      console.log("---->", value, oldValue)
    }
    x.value = value[0] * 200
  })

  function loadVideo(_src: string) {
    src.value = _src
    videoRef.value?.load()
  }

  const seek = (sec: number) => {
    currentTime.value = sec
  }
  const play = () => {
    playing.value = true
  }
  const pause = () => {
    playing.value = false
  }

  return {
    toggle,
    duration,
    videoRef,
    src,
    waiting,
    seek,
    playing,
    play,
    pause,
    volume,
    currentTime,
    seeking,
    loadVideo,
    togglePictureInPicture,
  }
})

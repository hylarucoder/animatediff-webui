export default defineComponent({
  setup() {
    const timelineStore = useTimelineStore()
    const { duration, refRuler, unitWidth, fps, isMouseOutside, rulerPos } = storeToRefs(timelineStore)
    const videoPlayerStore = useVideoPlayer()
    const playAxis = usePlayAxis()
    const { style, x: timeStartPx, el, isDragging } = storeToRefs(playAxis)

    const seek = useThrottleFn(() => {
      videoPlayerStore.seek(timeStartPx.value / 200)
    }, 500)

    watch([timeStartPx, isDragging], ([, isDraggingNow]) => {
      if (isDraggingNow) {
        seek()
      }
    })

    return () => (
      <div>
        <div ref={el} style={style.value} class="absolute z-[100] h-full w-px cursor-move bg-red-500">
          <svg
            class="absolute -left-[12px] -top-3 h-6 w-6 fill-current text-red-500"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 50 50"
          >
            <polygon points="25,40 0,10 50,10" fill="red" />
          </svg>
        </div>
        {isMouseOutside.value === false && (
          <div
            style={{ left: `${rulerPos.value}px` }}
            class="pointer-events-none absolute z-[90] h-full w-px bg-red-500"
          >
            <svg
              class="absolute -left-[12px] -top-3 h-6 w-8 fill-current text-gray-500"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 50 50"
            >
              <polygon points="25,40 0,10 50,10" fill="black" />
            </svg>
          </div>
        )}
        <div
          ref={refRuler}
          class="timeline relative h-[40px] select-none border-b-[1px] border-zinc-200"
          onClick={(e) => e.preventDefault() /* Replace with your actual click handler */}
        >
          {Array.from({ length: duration.value * fps.value }, (_, i) => (
            <div
              key={i}
              class="absolute z-[100] w-[25px]"
              style={{
                left: `${i * unitWidth.value}px`,
                width: `${unitWidth.value}px`,
              }}
            >
              {i % fps.value === 0 ? (
                <span class="text-ms block w-[25px] select-none font-semibold text-gray-600">{i / fps.value}s</span>
              ) : (
                <span
                  class="block select-none text-[10px] font-semibold text-gray-400"
                  style={{ width: `${unitWidth.value}px` }}
                >
                  |
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  },
})

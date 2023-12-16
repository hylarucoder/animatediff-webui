export default defineComponent({
  setup() {
    const timelineStore = useTimelineStore()
    const { leftPanelWidth } = storeToRefs(timelineStore)

    const optTimelines = [
      {
        title: "prompt",
      },
      // Uncomment or add more timelines as needed
      // {
      //   title: "ip-adapter",
      // },
      // {
      //   title: "depth",
      // },
    ]

    return () => (
      <div
        class="h-full select-none border-r-[1px] border-zinc-200"
        style={{
          width: leftPanelWidth.value + "px",
        }}
      >
        <div class="flex h-[40px] border-b-[1px] border-zinc-200 px-[8px] text-white" />
        {optTimelines.map((timeline, index) => (
          <div key={index} class="flex h-[40px] border-b-[1px] border-zinc-200 px-[8px] text-white">
            <div class="flex w-[80px] items-center justify-center overflow-ellipsis">
              <span class="line-clamp-1 block w-[80px] cursor-pointer text-center text-sm text-zinc-600">
                {timeline.title}
              </span>
            </div>
          </div>
        ))}
      </div>
    )
  },
})

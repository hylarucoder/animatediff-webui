import { VTimelineToolbar, VTimelineTrackLeftPanel, VTimelineTracks } from "#components"

export default defineComponent({
  setup() {
    // Use your timeline store
    const timeline = useTimelineStore()

    // Lifecycle hook: Before the component is mounted, initialize blocks in your timeline
    onBeforeMount(() => {
      timeline.initBlocks()
    })

    // TSX render function
    return () => (
      <div class="relative h-[--timeline-height] w-full overflow-scroll border-x-[1px] border-b-[1px] border-zinc-100 bg-zinc-50 p-0">
        {/* VTimeToolbar */}
        <VTimelineToolbar />
        <div class="flex w-full">
          {/* VTimelineTrackLeftPanel */}
          <VTimelineTrackLeftPanel />
          {/* VTimelineTracks */}
          <VTimelineTracks />
        </div>
      </div>
    )
  },
})

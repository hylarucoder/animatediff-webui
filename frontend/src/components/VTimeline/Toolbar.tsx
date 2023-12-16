import { APopover, VTimelineLayoutPopover } from "#components"

export default defineComponent({
  setup() {
    // Any reactive state or computed properties would go here

    return () => (
      <div class="flex h-[--timeline-toolbar-height] items-center border-b-[1px] border-zinc-200 px-2 pb-2 pt-2">
        <APopover placement="topLeft">
          {{
            content: () => <VTimelineLayoutPopover />,
            default: () => (
              <div class="flex items-center">
                <span class="i-lucide-layout h-4 w-4 text-zinc-600" />
              </div>
            ),
          }}
        </APopover>
      </div>
    )
  },
})

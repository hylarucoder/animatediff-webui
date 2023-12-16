import { ATabPane, ATabs, VFinder, VPlayer } from "#components"

export default defineComponent({
  setup() {
    const activeKey = ref("1")

    return () => (
      <div class="w-full overflow-auto border-x-[1px] border-b-[1px] border-zinc-100">
        <ATabs
          activeKey={activeKey.value}
          onUpdate:activeKey={(v) => {
            activeKey.value = v
          }}
          class="tab-main relative z-10"
        >
          <ATabPane key="1" tab="Player" class="relative h-full w-full">
            <VPlayer />
          </ATabPane>
          <ATabPane key="2" tab="Media" class="">
            {/* <VFinder */}
            {/*   id="media-finder" */}
            {/*   adapter="local" */}
            {/*   class="z-1100 h-[600px] w-full bg-white" */}
            {/*   url="http://localhost:8000/api/finder" */}
            {/* /> */}
          </ATabPane>
        </ATabs>
      </div>
    )
  },
})

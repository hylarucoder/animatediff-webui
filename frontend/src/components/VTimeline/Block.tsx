import type { TTrackBlock } from "~/composables/timeline"

export default defineComponent({
  props: {
    block: Object as () => TTrackBlock,
    isVirtual: Boolean,
    unitWidth: Number,
  },
  emits: ["blockSelect", "dragStart", "dragEnd"],
  setup(props, { emit }) {
    const block = ref(props.block)
    const isVirtual = ref(props.isVirtual)
    const left = computed(() => Math.floor(block.value.start / 5))
    const blockWidth = computed(() => 25)
    const selected = ref(false)

    const refBlock = ref<HTMLDivElement>()

    onClickOutside(refBlock, () => {
      selected.value = false
    })

    const onClickBlock = (block: TTrackBlock) => {
      selected.value = true
      emit("blockSelect", block)
    }

    const onDragEnd = (e: DragEvent) => {
      const target = e.target as HTMLElement
      const parentElement = target.parentElement

      if (!parentElement) {
        console.error("No parent element found")
        return
      }

      const rect = parentElement.getBoundingClientRect()
      const relativeMousePosition = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      }

      target.classList.add("dragend-animation")

      // Uncomment the following line if you want to remove the class after a delay
      // setTimeout(() => { target.classList.remove("dragend-animation") }, 500);

      emit("dragEnd", block.value, relativeMousePosition.x)
    }

    onMounted(() => {
      // Handle any setup that needs to occur once the component is mounted
    })

    return () => (
      <div
        ref={refBlock}
        class={{
          "timeline-track-block absolute m-0 flex h-[40px] items-center justify-center p-0 text-center": true,
          "border-2 border-white": selected.value && !isVirtual.value,
        }}
        style={{
          width: `${blockWidth.value}px`,
          left: `${left.value}px`,
        }}
        draggable
        onDragstart={() => emit("dragStart", block.value.start)}
        onDragend={onDragEnd}
        onClick={() => onClickBlock(block.value)}
      >
        <div
          class={{
            "mx-[1px] h-full text-xs": true,
            "bg-amber-500": !isVirtual.value,
            "bg-amber-300": isVirtual.value,
          }}
          style={{
            height: "calc(100% - 4px)",
            width: "calc(100% - 4px)",
          }}
        >
          T
        </div>
      </div>
    )
  },
})

import { defineComponent, computed } from "vue"

export default defineComponent({
  props: {
    index: {
      type: Number,
      required: true,
    },
    unitWidth: {
      type: Number,
      required: true,
    },
    fps: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    // Computed property to determine the label to be displayed
    const label = computed(() => {
      if (props.index % props.fps === 0) {
        return `${props.index / props.fps}s`
      } else {
        return "|"
      }
    })

    // Computed property for the style based on props
    const rulerStyle = computed(() => ({
      marginLeft: `${props.index * props.unitWidth}px`,
      width: `${props.unitWidth}px`,
    }))

    // Click handler function
    const onClickRuler = (e: MouseEvent) => {
      console.log("ruler", e)
    }

    // Render function using TSX
    return () => (
      <div class="absolute z-[10] select-none" onClick={onClickRuler} style={rulerStyle.value}>
        <span
          class={{
            "block text-[8px] font-semibold text-gray-400": props.index % props.fps !== 0,
            "block text-[10px] font-semibold text-gray-600": props.index % props.fps === 0,
          }}
          style={{ width: `${props.unitWidth}px` }}
        >
          {label.value}
        </span>
      </div>
    )
  },
})

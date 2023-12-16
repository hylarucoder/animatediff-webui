import type { PropType } from "vue"

export default defineComponent({
  props: {
    icon: {
      type: String as PropType<string>,
      required: true,
    },
    layout: {
      type: String as PropType<"left" | "right">,
      required: true,
    },
  },
  setup(props, { slots }) {
    // Use `toRefs` to create a reactive reference for each prop
    const { icon, layout } = storeToRefs(props)

    return () => (
      <div class="flex w-1/2">
        {layout.value === "left" ? (
          <>
            <div class="mr-2 flex items-center justify-center">
              <span class={[icon.value, "h-5 w-5 text-sm leading-6 text-zinc-600"]} />
            </div>
            {slots.default ? slots.default() : null}
          </>
        ) : (
          <>
            {slots.default ? slots.default() : null}
            <div class="ml-2 flex items-center justify-center">
              <span class={[icon.value, "h-5 w-5 text-sm leading-6 text-zinc-600"]} />
            </div>
          </>
        )}
      </div>
    )
  },
})

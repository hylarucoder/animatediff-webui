export default defineComponent({
  setup(props, { slots }) {
    return () => (
      <div class="mt-0 min-h-[600px] w-full min-w-[800px] overflow-hidden pb-0 dark:bg-zinc-800">
        {slots.default ? slots.default() : null}
      </div>
    )
  },
})

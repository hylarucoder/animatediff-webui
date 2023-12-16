import { AButton, AFormItem, AInput } from "#components"

export default defineComponent({
  setup() {
    return () => (
      <div class="min-h-full p-5">
        <AFormItem label="Controlnet">
          <AInput />
        </AFormItem>
        <AButton>Preview</AButton>
      </div>
    )
  },
})

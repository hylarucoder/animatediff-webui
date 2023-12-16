import { AButton, AForm, AFormItem, VPromptInput } from "#components"

export default defineComponent({
  setup() {
    const activeBlock = useActiveBlockStore()
    const { block, refInput } = toRefs(activeBlock)
    const { onFocus, onBlur, deleteBlock } = activeBlock

    onMounted(() => {
      if (refInput.value) {
        refInput.value.focus()
      }
    })

    return () => {
      if (!block.value) {
        return <div>error</div>
      } else {
        return (
          <div class="timeline-track-block-editor min-h-full w-full p-5">
            <AForm layout="vertical">
              <AFormItem label="Time"> {(block.value.start / 1000).toFixed(1)}s</AFormItem>
              <AFormItem label="Prompt">
                <VPromptInput
                  ref={refInput}
                  onFocus={onFocus}
                  onBlur={onBlur}
                  autoFocus
                  value={block.value.prompt}
                  onUpdate:value={(v) => {
                    block.value.prompt = v
                  }}
                />
              </AFormItem>
              <AButton onClick={deleteBlock}>Save</AButton>
            </AForm>
          </div>
        )
      }
    }
  },
})

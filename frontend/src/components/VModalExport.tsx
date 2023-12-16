import { AButton, AForm, AFormItem, AInputNumber, AModal, ARadio, ARadioGroup } from "#components"

export default defineComponent({
  setup(props, { emit }) {
    const storeVideoExport = useVideoExportStore()
    const { task, isActive } = storeToRefs(storeVideoExport)
    const optionsStore = useOptionsStore()
    const { optPerformances } = optionsStore
    const formStore = useFormStore()
    const { sizeOpts, size, duration, performance } = storeToRefs(formStore)

    const handleCloseModal = () => emit("closeModal")
    console.log("task", task.value)

    return () => (
      <AModal centered open title="Export" onClose={handleCloseModal}>
        {{
          default: () => (
            <div class="flex h-[400px] w-[500px] select-none">
              <div class="flex w-1/2 pr-5 pt-2">
                <div class="flex h-full w-full items-center justify-center bg-zinc-300">
                  <div class="flex-col">
                    <div>rendering</div>
                    <div>{JSON.stringify(task.value)}</div>
                  </div>
                </div>
              </div>
              <div class="flex w-1/2">
                <AForm layout="vertical">
                  <AFormItem label="Performance" required>
                    <ARadioGroup value={performance.value} onUpdate:value={(val) => (performance.value = val)}>
                      {optPerformances.map((opt) => (
                        <ARadio key={opt.value} value={opt.value} label={opt.label}>
                          {opt.label}
                        </ARadio>
                      ))}
                    </ARadioGroup>
                  </AFormItem>
                  <AFormItem label="Duration(s)" required>
                    <AInputNumber
                      value={duration.value}
                      class="text-left"
                      onUpdate:value={(val) => (duration.value = val)}
                    />
                  </AFormItem>
                  <AFormItem label="Output Size" required>
                    <ARadioGroup value={size.value} onUpdate:value={(val) => (size.value = val)}>
                      {sizeOpts.value.map((opt) => (
                        <ARadio key={opt.value} value={opt.value} label={opt.label}>
                          {opt.label}
                        </ARadio>
                      ))}
                    </ARadioGroup>
                  </AFormItem>
                </AForm>
              </div>
            </div>
          ),
          footer: () => (
            <>
              <AButton key="back" onClick={handleCloseModal}>
                Return
              </AButton>
              <AButton
                key="submit"
                type="primary"
                loading={isActive.value}
                onClick={() => {
                  console.log("oncli")
                  storeVideoExport.submitExport()
                }}
              >
                Export
              </AButton>
            </>
          ),
        }}
      </AModal>
    )
  },
})

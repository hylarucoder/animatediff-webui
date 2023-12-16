import { AForm, AFormItem, AInputNumber, ATabPane, ATabs, VPreviewSelect, VPromptInput } from "#components"

export default defineComponent({
  setup() {
    const optionsStore = useOptionsStore()
    const { optLoras, optCheckpoints } = storeToRefs(optionsStore)
    const formStore = useFormStore()
    const { checkpoint, prompt, negativePrompt, seed, fps, loras } = storeToRefs(formStore)

    const advanced = ref({
      cfg: 1,
    })
    const activeKey = ref("1")

    return () => (
      <ATabs
        activeKey={activeKey.value}
        onUpdate:activeKey={(v) => {
          activeKey.value = v
        }}
        class="relative z-0"
      >
        <ATabPane key="1" tab="Setting" class="max-w-[500px]">
          <AForm layout="vertical" class="form-compact mt-4">
            <AFormItem label="Prompt">
              <VPromptInput
                v-model:value={prompt.value}
                onUpdate:value={(value) => {
                  prompt.value = value
                }}
              />
            </AFormItem>
            <AFormItem label="Negative Prompt">
              <VPromptInput
                value={negativePrompt.value}
                onUpdate:value={(value) => {
                  negativePrompt.value = value
                }}
              />
            </AFormItem>
            <AForm layout="vertical">
              <AFormItem label="Checkpoint">
                <VPreviewSelect
                  value={checkpoint.value}
                  onUpdate:value={(value) => {
                    checkpoint.value = value
                  }}
                  options={optCheckpoints.value}
                />
              </AFormItem>
            </AForm>
            <AForm layout="vertical">
              <AFormItem label="LoRAs">
                {loras.value.map((opt, idx) => (
                  <div key={idx} class="mb-2 flex">
                    <VPreviewSelect
                      value={opt.name}
                      onUpdate:value={(value) => {
                        opt.name = value
                      }}
                      class="w-[120px] min-w-[120px]"
                      options={optLoras.value}
                    />
                    <AInputNumber
                      value={opt.weight}
                      onUpdate:value={(value) => {
                        opt.weight = value
                      }}
                      min={0}
                      max={2}
                      step={0.1}
                      class="ml-2"
                    />
                  </div>
                ))}
              </AFormItem>
            </AForm>
          </AForm>
        </ATabPane>
        <ATabPane key="2" tab="Advanced">
          <AForm layout="vertical" class="form-compact mt-4">
            <AFormItem label="Seed">
              <AInputNumber
                value={seed.value}
                onUpdate:value={(v) => {
                  seed.value = v
                }}
                step={1}
              />
            </AFormItem>
            <AFormItem label="FPS">
              <AInputNumber
                value={fps.value}
                onUpdate:value={(v) => {
                  fps.value = v
                }}
                step={1}
                min={4}
                max={16}
              />
            </AFormItem>
          </AForm>
        </ATabPane>
      </ATabs>
    )
  },
})

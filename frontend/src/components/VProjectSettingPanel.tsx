import { AForm, AFormItem, AInputNumber, ATabPane, ATabs, VPreviewSelect, VPromptInput } from "#components"
import { algorithms } from "iron-webcrypto"

export default defineComponent({
  setup() {
    const optionsStore = useOptionsStore()
    const { optLoras, optCheckpoints } = storeToRefs(optionsStore)
    const formStore = useFormStore()
    const { highRes, checkpoint, prompt, negativePrompt, seed, duration, fps, loras, cameraControl } =
      storeToRefs(formStore)

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
              <VPromptInput v-model={[prompt.value, "value"]} />
            </AFormItem>
            <AFormItem label="Negative Prompt">
              <VPromptInput v-model={[negativePrompt.value, "value"]} />
            </AFormItem>
            <AForm layout="vertical">
              <AFormItem label="Checkpoint">
                <VPreviewSelect v-model={[checkpoint.value, "value"]} options={optCheckpoints.value} />
              </AFormItem>
            </AForm>
            <AForm layout="vertical">
              <AFormItem label="LoRAs">
                {loras.value.map((opt, idx) => (
                  <div key={idx} class="mb-2 flex">
                    <VPreviewSelect
                      v-model={[opt.name, "value"]}
                      class="w-[120px] min-w-[120px]"
                      options={optLoras.value}
                    />
                    <AInputNumber v-model={[opt.weight, "value"]} min={0} max={2} step={0.1} class="ml-2" />
                  </div>
                ))}
              </AFormItem>
            </AForm>
          </AForm>
        </ATabPane>
        <ATabPane key="2" tab="Advanced">
          <AForm layout="vertical" class="form-compact mt-4">
            <AFormItem label="Seed">
              <AInputNumber v-model={[seed.value, "value"]} step={1} />
            </AFormItem>
            <AFormItem label="FPS">
              <AInputNumber v-model={[fps.value, "value"]} step={1} min={4} max={16} />
            </AFormItem>
          </AForm>
        </ATabPane>
      </ATabs>
    )
  },
})

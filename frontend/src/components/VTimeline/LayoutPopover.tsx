import { CONTROLNETS } from "~/consts"
import { ACheckbox, ACheckboxGroup, AForm } from "#components"

export default defineComponent({
  setup() {
    const labelCol = { style: { width: "100px" } }
    const wrapperCol = { span: 14 }

    const cleanLabel = (label: string) => {
      return label.replaceAll("controlnet_", "")
    }

    const timelineStore = useTimelineStore()
    const { timeline } = storeToRefs(timelineStore)

    return () => (
      <div class="w-[400px]">
        <AForm layout="vertical" model={timeline.value} labelCol={labelCol} wrapperCol={wrapperCol}>
          <AForm-item label="controlnet">
            <ACheckboxGroup
              value={timeline.value.controlnet}
              onUpdate:value={(v) => {
                timeline.value.controlnet = v
              }}
            >
              {CONTROLNETS.map((cn) => (
                <ACheckbox value={cn} name="controlnet">
                  {cleanLabel(cn)}
                </ACheckbox>
              ))}
            </ACheckboxGroup>
          </AForm-item>
          <AForm-item label="ip-adapter">
            <ACheckboxGroup
              onUpdate:value={(v) => {
                timeline.value.ipAdapter = v
              }}
              value={timeline.value.ipAdapter}
            >
              <ACheckbox value="ipadapter" name="type">
                IPAdapter
              </ACheckbox>
            </ACheckboxGroup>
          </AForm-item>
        </AForm>
      </div>
    )
  },
})

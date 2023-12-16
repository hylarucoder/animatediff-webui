import { defineComponent, toRefs } from "vue"
import { useTimelineStore } from "~/composables/timeline" // Assumed import
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
    const { timeline } = toRefs(timelineStore)

    return () => (
      <div class="w-[400px]">
        <AForm layout="vertical" model={timeline.value} labelCol={labelCol} wrapperCol={wrapperCol}>
          <AForm-item label="controlnet">
            <ACheckbox-group v-model={timeline.value.controlnet}>
              {CONTROLNETS.map((cn) => (
                <ACheckbox value={cn} name="controlnet">
                  {cleanLabel(cn)}
                </ACheckbox>
              ))}
            </ACheckbox-group>
          </AForm-item>
          <AForm-item label="ip-adapter">
            <ACheckboxGroup v-model={timeline.value.ipAdapter}>
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

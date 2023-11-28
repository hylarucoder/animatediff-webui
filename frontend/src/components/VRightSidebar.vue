<script setup lang="ts">

const {
  options,
} = useStore()
const { form } = useAnimateForm()
console.log(options.value)

const unflatten = (arr: any[]) => {
  return arr.map((x) => {
    return {
      label: x,
      value: x,
    }
  })
}

const unflattenCheckpoint = (arr: any[]) => {
  return arr.map((x) => {
    return {
      label: x.name,
      value: x.name,
    }
  })
}
const perfOptions = unflatten(performances)

const aspectRadioOptions = unflatten(aspect_ratios)

const checkpointOptions = unflattenCheckpoint(options.value.checkpoints)

const motionOptions = unflattenCheckpoint(options.value.motions)
const motionLorasOptions = unflattenCheckpoint(options.value.motion_loras)
const lorasOptions = unflattenCheckpoint(options.value.loras)
console.log(perfOptions, checkpointOptions, lorasOptions, toRaw(options.value))

const advanced = ref({
  cfg: 1,
})
const activeKey = ref("1")

</script>
<template>
  <div class="w-[500px] h-[800px] border-gray-200 border-r-[1px] border-b-[1px] py-2 px-5">
    <a-tabs v-model:activeKey="activeKey">
      <a-tab-pane key="1" tab="Setting">
        <AForm
            layout="vertical"
        >
          <a-form-item
              label="Performance"
          >
            <a-radio-group
                v-model:value="form.performance"
            >
              <a-radio
                  v-for="_ in perfOptions"
                  :key="_.value"
                  :value="_.value"
                  :label="_.label"
              > {{ _.value }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item
              label="Aspect Radios"
          >
            <a-radio-group
                v-model:value="form.aspect_ratio"
            >
              <a-radio
                  v-for="ar in aspectRadioOptions"
                  :key="ar.value"
                  class="font-mono"
                  :value="ar.value"
                  :label="ar.label"
              >{{ ar.value }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item
              label="Head Prompt"
          >
            <a-input :value="form.head_prompt"/>
          </a-form-item>
          <a-form-item
              label="Tail Prompt"
          >
            <a-textarea
                v-model:value="form.tail_prompt"
            />
          </a-form-item>
          <a-form-item
              label="Negative Prompt"
          >
            <a-textarea
                v-model:value="form.negative_prompt"
            />
          </a-form-item>
          <a-form-item
              label="Seed"
          >
            <a-input-number v-model:value="form.seed" step="1"/>
          </a-form-item>
          <div class="flex space-x-5">
            <a-form-item
                label="Duration(s)"
            >
              <a-input-number
                  step="1"
                  min="1"
                  max="600"
                  v-model:value="form.duration"
              />
            </a-form-item>
            <a-form-item
                label="FPS"
            >
              <a-input-number
                  step="1"
                  min="4"
                  max="16"
                  v-model:value="form.fps"
              />
            </a-form-item>
          </div>
        </AForm>
      </a-tab-pane>
      <a-tab-pane key="2" tab="Model">
        <a-form
            layout="vertical"
        >
          <a-form-item
              label="Checkpoint"
          >
            <a-select
                v-model:value="form.checkpoint"
                :options="checkpointOptions"
            />
          </a-form-item>
        </a-form>
        <a-form
            layout="vertical"
        >
          <a-form-item
              v-for="(song, idx) in form.loras"
              class="form-item-no-feedback"
              :label="`LoRA ${idx + 1}`"
          >
            <div class="flex">
              <a-select
                  v-model:value="song.name"
                  size="small"
                  class="w-[150px] min-w-[150px]"
                  :options="lorasOptions"
              />
              <a-input-number
                  v-model:value="song.weight"
                  size="small"
                  min="0"
                  max="2"
                  step="0.1"
                  class="ml-2"
              />
            </div>
          </a-form-item>
          <a-form
              class="pt-5"
              layout="vertical"
          >
            <a-form-item
                label="Motion"
            >
              <a-select
                  v-model:value="form.motion"
                  :options="motionOptions"
              />
            </a-form-item>
            <a-form-item
                label="Motion LoRAs"
            >
              <a-select
                  v-model:value="form.motion_lora"
                  :options="motionLorasOptions"
              />
            </a-form-item>
          </a-form>
        </a-form>
      </a-tab-pane>
      <a-tab-pane key="3" tab="Advanced">
        <a-form-item
            label="cfg"
            size="small"
        >
          <a-slider
              v-model:value="advanced.cfg"
          />
        </a-form-item>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<style>
.form-item-no-feedback .n-form-item-feedback-wrapper {
  display: none;
}
</style>

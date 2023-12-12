<script setup lang="ts">
const optionsStore = useOptionsStore()
const { optPerformances, optLoras, optCheckpoints, optAspectRadios, optMotionLoras } = optionsStore
const formStore = useFormStore()
const {
  performance,
  highRes,
  checkpoint,
  aspectRatio,
  prompt,
  negativePrompt,
  seed,
  duration,
  fps,
  loras,
  cameraControl,
} = storeToRefs(formStore)

const advanced = ref({
  cfg: 1,
})
const activeKey = ref("1")
</script>
<template>
  <a-tabs v-model:activeKey="activeKey" class="relative z-0">
    <a-tab-pane key="1" tab="Setting" class="max-w-[500px]">
      <a-form layout="vertical" class="form-compact">
        <a-form-item label="Performance">
          <a-radio-group v-model:value="performance">
            <a-radio v-for="opt in optPerformances" :key="opt.value" :value="opt.value" :label="opt.label">
              {{ opt.label }}
            </a-radio>
          </a-radio-group>
        </a-form-item>
        <div class="flex w-full items-start">
          <a-form-item label="Aspect Radios">
            <a-radio-group v-model:value="aspectRatio">
              <a-radio
                v-for="ar in optAspectRadios"
                :key="ar.value"
                class="font-mono"
                :value="ar.value"
                :label="ar.label"
              >
                {{ ar.value }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-checkbox v-model:checked="highRes"> HiRes</a-checkbox>
        </div>
        <a-form-item label="Prompt">
          <v-prompt-input v-model:value="prompt" />
        </a-form-item>
        <a-form-item label="Negative Prompt">
          <v-prompt-input v-model:value="negativePrompt" />
        </a-form-item>
        <a-form-item label="Seed">
          <a-input-number v-model:value="seed" step="1" />
        </a-form-item>
        <div class="flex space-x-5">
          <a-form-item label="Duration(s)">
            <a-input-number v-model:value="duration" step="1" min="1" max="600" />
          </a-form-item>
          <a-form-item label="FPS">
            <a-input-number v-model:value="fps" step="1" min="4" max="16" />
          </a-form-item>
        </div>
      </a-form>
    </a-tab-pane>
    <a-tab-pane key="2" class="w-[300px]" tab="Model">
      <a-form layout="vertical">
        <a-form-item label="Checkpoint">
          <v-preview-select v-model:value="checkpoint" :options="optCheckpoints" />
        </a-form-item>
      </a-form>
      <a-form size="small" layout="vertical">
        <a-form-item v-for="(opt, idx) in loras" :key="idx" class="form-item-thin-margin" :label="`LoRA ${idx + 1}`">
          <div class="flex">
            <v-preview-select v-model:value="opt.name" class="w-[150px] min-w-[150px]" :options="optLoras" />
            <a-input-number v-model:value="opt.weight" size="small" min="0" max="2" step="0.1" class="ml-2" />
          </div>
        </a-form-item>
        <a-form class="pt-5" layout="vertical" size="small">
          <a-form-item label="Camera Control" class="camera-control-title">
            <div class="mt-5 flex justify-between space-x-8">
              <a-form-item label="Pan Left" class="w-1/2">
                <a-slider v-model:value="cameraControl.panLeft" :min="0" :max="1" :step="0.1" reverse />
              </a-form-item>
              <a-form-item label="Pan Right" class="w-1/2">
                <a-slider v-model:value="cameraControl.panRight" :min="0" :max="1" :step="0.1" />
              </a-form-item>
            </div>
            <div class="flex justify-between space-x-8">
              <a-form-item label="Tile Up" class="w-1/2">
                <a-slider v-model:value="cameraControl.tileUp" :min="0" :max="1" :step="0.1" reverse />
              </a-form-item>
              <a-form-item label="Tile Down" class="w-1/2">
                <a-slider v-model:value="cameraControl.tileDown" :min="0" :max="1" :step="0.1" />
              </a-form-item>
            </div>
            <div class="flex justify-between space-x-8">
              <a-form-item label="Rolling Clockwise" class="w-1/2">
                <a-slider v-model:value="cameraControl.rollingClockwise" :min="0" :max="1" :step="0.1" reverse />
              </a-form-item>
              <a-form-item label="Anti Clockwise" class="w-1/2">
                <a-slider v-model:value="cameraControl.rollingAnticlockwise" :min="0" :max="1" :step="0.1" />
              </a-form-item>
            </div>
            <div class="flex justify-between space-x-8">
              <a-form-item label="Zoom In" class="w-1/2">
                <a-slider v-model:value="cameraControl.zoomIn" :min="0" :max="1" :step="0.1" reverse />
              </a-form-item>
              <a-form-item label="Zoom Out" class="w-1/2">
                <a-slider v-model:value="cameraControl.zoomOut" :min="0" :max="1" :step="0.1" />
              </a-form-item>
            </div>
          </a-form-item>
        </a-form>
      </a-form>
    </a-tab-pane>
    <a-tab-pane key="3" tab="Advanced">
      <a-form-item label="cfg" size="small">
        <a-slider v-model:value="advanced.cfg" />
      </a-form-item>
    </a-tab-pane>
  </a-tabs>
</template>

<style lang="scss">
.form-item-thin-margin.ant-form-item {
  margin-bottom: 5px !important;
}

.form-compact {
  .ant-form-item-label {
    margin-bottom: 0 !important;
  }

  .ant-form-item {
    margin-bottom: 8px !important;
  }
}

.camera-control-title {
  .ant-form-item-label {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
  }

  .ant-form-item {
    margin-bottom: 0 !important;

    label {
      font-size: 12px !important;
    }
  }
}
</style>

<script setup lang="ts">
const optionsStore = useOptionsStore()
const { optPerformances, optLoras, optMotions, optCheckpoints, optAspectRadios, optMotionLoras } = optionsStore
const formStore = useFormStore()
const { performance, checkpoint, aspectRatio, prompt, negativePrompt, seed, duration, fps, loras, motion, motionLora } =
  storeToRefs(formStore)

const advanced = ref({
  cfg: 1,
})
const activeKey = ref("1")
</script>
<template>
  <a-tabs v-model:activeKey="activeKey" class="relative z-10">
    <a-tab-pane key="1" tab="Setting" class="max-w-[500px]">
      <AForm layout="vertical">
        <a-form-item label="Performance">
          <a-radio-group v-model:value="performance">
            <a-radio v-for="opt in optPerformances" :key="opt.value" :value="opt.value" :label="opt.label">
              {{ opt.label }}
            </a-radio>
          </a-radio-group>
        </a-form-item>
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
        <a-form-item label="Prompt">
          <a-textarea v-model:value="prompt" />
        </a-form-item>
        <a-form-item label="Negative Prompt">
          <a-textarea v-model:value="negativePrompt" />
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
      </AForm>
    </a-tab-pane>
    <a-tab-pane key="2" class="w-[300px]" tab="Model">
      <a-form layout="vertical">
        <a-form-item label="Checkpoint">
          <v-preview-select v-model:value="checkpoint" :options="optCheckpoints" />
        </a-form-item>
      </a-form>
      <a-form layout="vertical">
        <a-form-item v-for="(opt, idx) in loras" :key="idx" class="form-item-no-feedback" :label="`LoRA ${idx + 1}`">
          <div class="flex">
            <v-preview-select v-model:value="opt.name" class="w-[150px] min-w-[150px]" :options="optLoras" />
            <a-input-number v-model:value="opt.weight" size="small" min="0" max="2" step="0.1" class="ml-2" />
          </div>
        </a-form-item>
        <a-form class="pt-5" layout="vertical">
          <a-form-item label="Motion">
            <a-select v-model:value="motion" show-search :options="optMotions" />
          </a-form-item>
          <a-form-item label="Motion LoRAs">
            <a-select v-model:value="motionLora" show-search :options="optMotionLoras" />
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

<style>
.form-item-no-feedback .n-form-item-feedback-wrapper {
  display: none;
  margin-bottom: 0 !important;
}
</style>

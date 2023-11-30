<script setup lang="ts">
const optionsStore = useOptionsStore()
const { options, optPerformances, optLoras, optMotions, optCheckpoints, optAspectRadios, optMotionLoras } = optionsStore
const formStore = useFormStore()
const {
  performance,
  checkpoint,
  aspect_ratio,
  head_prompt,
  tail_prompt,
  negative_prompt,
  seed,
  duration,
  fps,
  loras,
  motion,
  motion_lora,
} = formStore

const advanced = ref({
  cfg: 1,
})
const activeKey = ref("1")
</script>
<template>
  <div class="h-[800px] w-[400px] overflow-auto border-b-[1px] border-r-[1px] border-gray-200 px-5 py-2">
    <a-tabs v-model:activeKey="activeKey">
      <a-tab-pane key="1" tab="Setting" class="max-w-[500px]">
        <AForm layout="vertical">
          <a-form-item label="Performance">
            <a-radio-group v-model:value="performance">
              <a-radio v-for="opt in optPerformances" :key="opt.value" :value="opt.value" :label="opt.label">
                {{ opt.value }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="Aspect Radios">
            <a-radio-group v-model:value="aspect_ratio">
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
          <a-form-item label="Head Prompt">
            <a-input :value="head_prompt" />
          </a-form-item>
          <a-form-item label="Tail Prompt">
            <a-textarea v-model:value="tail_prompt" />
          </a-form-item>
          <a-form-item label="Negative Prompt">
            <a-textarea v-model:value="negative_prompt" />
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
      <a-tab-pane class="w-[300px]" key="2" tab="Model">
        <a-form layout="vertical">
          <a-form-item label="Checkpoint">
            <a-select show-search v-model:value="checkpoint" :options="optCheckpoints" />
          </a-form-item>
        </a-form>
        <a-form layout="vertical">
          <a-form-item v-for="(opt, idx) in loras" :key="idx" class="form-item-no-feedback" :label="`LoRA ${idx + 1}`">
            <div class="flex">
              <a-select show-search v-model:value="opt.name" class="w-[150px] min-w-[150px]" :options="optLoras" />
              <a-input-number v-model:value="opt.weight" size="small" min="0" max="2" step="0.1" class="ml-2" />
            </div>
          </a-form-item>
          <a-form class="pt-5" layout="vertical">
            <a-form-item label="Motion">
              <a-select show-search v-model:value="motion" :options="optMotions" />
            </a-form-item>
            <a-form-item label="Motion LoRAs">
              <a-select show-search v-model:value="motion_lora" :options="optMotionLoras" />
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
  </div>
</template>

<style>
.form-item-no-feedback .n-form-item-feedback-wrapper {
  display: none;
}
</style>

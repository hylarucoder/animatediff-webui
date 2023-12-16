<script setup lang="ts">
const optionsStore = useOptionsStore()
const { optLoras, optCheckpoints } = storeToRefs(optionsStore)
const formStore = useFormStore()
const { highRes, checkpoint, prompt, negativePrompt, seed, duration, fps, loras, cameraControl } =
  storeToRefs(formStore)

const advanced = ref({
  cfg: 1,
})
const activeKey = ref("1")
console.log("op cp", optCheckpoints)
</script>
<template>
  <a-tabs v-model:activeKey="activeKey" class="relative z-0">
    <a-tab-pane key="1" tab="Setting" class="max-w-[500px]">
      <a-form layout="vertical" class="form-compact mt-4">
        <a-form-item label="Prompt">
          <v-prompt-input v-model:value="prompt" />
        </a-form-item>
        <a-form-item label="Negative Prompt">
          <v-prompt-input v-model:value="negativePrompt" />
        </a-form-item>
        <a-form layout="vertical">
          <a-form-item label="Checkpoint">
            <v-preview-select v-model:value="checkpoint" :options="optCheckpoints" />
          </a-form-item>
        </a-form>
        <a-form layout="vertical">
          <a-form-item label="LoRAs">
            <div v-for="(opt, idx) in loras" :key="idx" class="mb-2 flex">
              <v-preview-select v-model:value="opt.name" class="w-[120px] min-w-[120px]" :options="optLoras" />
              <a-input-number v-model:value="opt.weight" min="0" max="2" step="0.1" class="ml-2" />
            </div>
          </a-form-item>
        </a-form>
      </a-form>
    </a-tab-pane>
    <a-tab-pane key="2" tab="Advanced">
      <a-form layout="vertical" class="form-compact mt-4">
        <a-form-item label="Seed">
          <a-input-number v-model:value="seed" step="1" />
        </a-form-item>
        <a-form-item label="FPS">
          <a-input-number v-model:value="fps" step="1" min="4" max="16" />
        </a-form-item>
      </a-form>
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

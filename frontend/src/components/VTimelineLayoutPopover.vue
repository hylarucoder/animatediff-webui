<script setup lang="ts">
import { CONTROLNETS } from "~/consts"

const labelCol = { style: { width: "100px" } }
const wrapperCol = { span: 14 }

const cleanLabel = (label) => {
  return label.replaceAll("controlnet_", "")
}
const timelineStore = useTimelineStore()
const { timeline } = storeToRefs(timelineStore)
</script>
<template>
  <div class="w-[400px]">
    <a-form layout="vertical" :model="timeline" :label-col="labelCol" :wrapper-col="wrapperCol">
      <a-form-item label="controlnet">
        <a-checkbox-group v-model:value="timeline.controlnet">
          <a-checkbox v-for="cn in CONTROLNETS" :value="cn" name="controlnet">{{ cleanLabel(cn) }}</a-checkbox>
        </a-checkbox-group>
      </a-form-item>
      <a-form-item label="ip-adapter">
        <a-checkbox-group v-model:value="timeline.ipAdapter">
          <a-checkbox value="ipadapter" name="type">IPAdapter</a-checkbox>
        </a-checkbox-group>
      </a-form-item>
    </a-form>
  </div>
</template>

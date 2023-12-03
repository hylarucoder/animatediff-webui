<script setup lang="ts">
import { CONTROLNETS } from "~/consts"

const labelCol = { style: { width: "100px" } }
const wrapperCol = { span: 14 }

const cleanLabel = (label) => {
  return label.replaceAll("controlnet_", "")
}
const timelineView = useTimeline()
</script>
<template>
  <a-form :model="timelineView.timeline" :label-col="labelCol" :wrapper-col="wrapperCol">
    <a-form-item label="Controlnet">
      <a-checkbox-group v-model:value="timelineView.timeline.controlnet">
        <a-checkbox v-for="cn in CONTROLNETS" :value="cn" name="controlnet">{{ cleanLabel(cn) }}</a-checkbox>
      </a-checkbox-group>
    </a-form-item>
    <a-form-item label="IPAdapter">
      <a-checkbox-group v-model:value="timelineView.timeline.ipAdapter">
        <a-checkbox value="ipadapter" name="type">IPAdapter</a-checkbox>
      </a-checkbox-group>
    </a-form-item>
  </a-form>
</template>

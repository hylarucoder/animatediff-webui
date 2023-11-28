<script setup lang="ts">
import { urlPrefix } from "~/consts"

const {
  setOptions,
} = useStore()
const {
  form,
  setPreset,
} = useAnimateForm()

// const { data, pending, error, refresh } = await useFetch(urlPrefix + `/api/options`, {
//   onResponse({ request, response, options }) {
//     const preset_name = response._data.presets[0].name
//     form.value.preset = preset_name
//     const preset = response._data.presets.find((p) => p.name === preset_name)
//     setPreset(preset)
//     form.value.checkpoint = response._data.checkpoints[0].name
//     form.value.motion = response._data.motions[0].name
//     setOptions(response._data)
//   },
// })
</script>
<template>
<!--  <div v-if="error">error</div>-->
<!--  <div v-if="pending">loading</div>-->
  <div class="w-full p-0 px-8">
    <VTopbar class="border-1"/>
    <div class="flex justify-between border-x-1 border-b-1">
      <VMainPlayer/>
      <VRightSidebar/>
    </div>
  </div>
</template>


<script setup lang="ts">
const props = defineProps({
  index: {
    type: Number,
    required: true,
  },
  unitWidth: {
    type: Number,
    required: true,
  },
  fps: {
    type: Number,
    required: true,
  },
})

const index = ref(props.index)
const unitWidth = ref(props.unitWidth)
const fps = ref(props.fps)
const onClickRuler = (e) => {
  console.log("ruler", e)
}
</script>
<template>
  <div
    class="absolute z-[10] select-none"
    @click="onClickRuler"
    :style="{
      marginLeft: index * unitWidth + 'px',
      width: unitWidth + 'px',
    }"
  >
    <span v-if="index % fps" class="block text-[8px] font-semibold text-gray-400" :style="{ width: unitWidth + 'px' }">
      |
    </span>
    <span v-else class="block text-[10px] font-semibold text-gray-600" :style="{ width: unitWidth + 'px' }">
      {{ index / fps }}s
    </span>
  </div>
</template>

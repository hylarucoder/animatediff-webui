<script lang="ts" setup>
import { formatProxyMedia } from "~/client"

interface TOptions {
  value: string
  label: string
  thumbnail?: string
}

const props = defineProps({
  value: {
    type: String,
    default: "",
  },
  options: {
    type: Array<TOptions>,
    default: () => [],
  },
})

const emit = defineEmits(["update:value"])

const selectedValue = ref(props.value)

// Watch for changes in the v-model and emit event
watch(selectedValue, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    emit("update:value", newVal)
  }
})
</script>
<template>
  <a-select v-model:value="selectedValue" show-search>
    <a-select-option
      v-for="opt in options"
      :key="opt.value"
      :value="opt.value"
      :label="opt.label"
      :title="opt.label"
      style="width: 100%"
    >
      <a-popover
        v-if="opt.thumbnail"
        :mouse-enter-delay="0.02"
        style="z-index: 1000"
        class="rounded-xl p-0"
        placement="right"
      >
        <template #content>
          <img class="max-w-[300px]" :src="formatProxyMedia(opt.thumbnail)" />
        </template>
        <span>{{ opt.label }}</span>
      </a-popover>
      <span v-else>{{ opt.label }}</span>
    </a-select-option>
  </a-select>
</template>

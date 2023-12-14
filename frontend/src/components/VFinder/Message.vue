<template>
  <div>
    <div
      v-if="!hidden"
      ref="strMessage"
      class="mt-1 flex rounded p-1 px-2 text-sm"
      :class="error ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'"
    >
      <slot />
      <div
        class="ml-auto cursor-pointer"
        :aria-label="t('Close')"
        data-microtip-position="top-left"
        role="tooltip"
        @click="hide"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="h-5 w-5"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script></script>

<script setup lang="ts">
const { t } = inject("i18n")
const props = defineProps({
  error: {
    type: Boolean,
    default: false,
  },
})

const hidden = ref(false)
const strMessage = ref(null)
const strSlot = ref(strMessage.value?.strMessage)
const emit = defineEmits(["hidden"])

watch(strSlot, () => (hidden.value = false))

const hide = () => {
  emit("hidden")
  hidden.value = true
}
</script>

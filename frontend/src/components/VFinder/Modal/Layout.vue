<template>
  <!-- This example requires Tailwind CSS v2.0+ -->
  <a-modal :open="true" @close="emitter.emit('vf-modal-close')" @keyup.esc="emitter.emit('vf-modal-close')">
    <div class="z-[1000] bg-white px-4 pb-4 pt-5 dark:bg-gray-800 sm:p-6 sm:pb-4">
      <slot />
    </div>
    <template #footer>
      <slot name="buttons" />
    </template>
  </a-modal>
</template>

<script setup>
const emitter = inject("emitter")

onMounted(() => {
  const inputElements = document.querySelector(".v-f-modal input")
  if (inputElements) {
    inputElements.focus()
  }
})
</script>

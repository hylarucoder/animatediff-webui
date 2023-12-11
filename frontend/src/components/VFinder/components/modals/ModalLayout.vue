<template>
  <!-- This example requires Tailwind CSS v2.0+ -->
  <div
    class="v-f-modal relative z-30"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
    @keyup.esc="emitter.emit('vf-modal-close')"
    tabindex="0"
  >
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity dark:bg-gray-600 dark:bg-opacity-75"></div>

    <div class="fixed inset-0 z-10 overflow-hidden">
      <div
        class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0"
        @mousedown.self="emitter.emit('vf-modal-close')"
      >
        <div
          class="relative w-full transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all dark:bg-gray-800 sm:my-8 sm:max-w-4xl md:max-w-2xl lg:max-w-3xl xl:max-w-5xl"
        >
          <div class="bg-white px-4 pb-4 pt-5 dark:bg-gray-800 sm:p-6 sm:pb-4">
            <slot />
          </div>
          <div
            class="bg-gray-50 px-4 py-3 dark:border-t dark:border-gray-700 dark:bg-gray-800 sm:flex sm:flex-row-reverse sm:px-6"
          >
            <slot name="buttons" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, onMounted } from "vue"

const emitter = inject("emitter")

onMounted(() => {
  const inputElements = document.querySelector(".v-f-modal input")
  if (inputElements) {
    inputElements.focus()
  }
})
</script>

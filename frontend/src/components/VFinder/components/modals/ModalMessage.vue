<template>
  <v-f-modal-layout>
    <div class="sm:flex sm:items-start">
      <div
        class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-blue-50 dark:bg-gray-500 sm:mx-0 sm:h-10 sm:w-10"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-6 w-6 stroke-blue-600 dark:stroke-blue-100"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <div class="mt-3 w-full text-center sm:ml-4 sm:mt-0 sm:text-left">
        <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-400" id="modal-title">
          {{ selection?.title ?? "Title" }}
        </h3>
        <div class="mt-2">
          <p class="text-sm text-gray-500">{{ selection?.message ?? "Message" }}.</p>
        </div>
      </div>
    </div>

    <template v-slot:buttons>
      <button
        type="button"
        @click="emitter.emit('vf-modal-close')"
        class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:ml-3 sm:mt-0 sm:w-auto sm:text-sm"
      >
        {{ t("Close") }}
      </button>
    </template>
  </v-f-modal-layout>
</template>

<script>
export default {
  name: "VFModalMessage",
}
</script>

<script setup>
import VFModalLayout from "./ModalLayout.vue"
import { inject } from "vue"
const emitter = inject("emitter")
const { t } = inject("i18n")

const props = defineProps({
  selection: Object,
})
</script>

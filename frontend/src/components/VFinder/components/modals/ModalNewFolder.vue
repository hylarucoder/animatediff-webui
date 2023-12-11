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
          stroke="none"
          stroke-width="1.5"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
          />
        </svg>
      </div>
      <div class="mt-3 w-full text-center sm:ml-4 sm:mt-0 sm:text-left">
        <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-400" id="modal-title">
          {{ t("New Folder") }}
        </h3>
        <div class="mt-2">
          <p class="text-sm text-gray-500">{{ t("Create a new folder") }}</p>
          <input
            v-model="name"
            @keyup.enter="createFolder"
            class="w-full rounded border px-2 py-1 dark:bg-gray-700/25 dark:text-gray-100 dark:focus:border-gray-600 dark:focus:ring-gray-600"
            :placeholder="t('Folder Name')"
            type="text"
          />
          <message v-if="message.length" @hidden="message = ''" error>{{ message }}</message>
        </div>
      </div>
    </div>

    <template v-slot:buttons>
      <button
        type="button"
        @click="createFolder"
        class="inline-flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:bg-gray-700 dark:hover:bg-gray-600/75 sm:ml-3 sm:w-auto sm:text-sm"
      >
        {{ t("Create") }}
      </button>
      <button
        type="button"
        @click="emitter.emit('vf-modal-close')"
        class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:ml-3 sm:mt-0 sm:w-auto sm:text-sm"
      >
        {{ t("Cancel") }}
      </button>
    </template>
  </v-f-modal-layout>
</template>

<script>
export default {
  name: "VFModalNewFolder",
}
</script>

<script setup>
import VFModalLayout from "./ModalLayout.vue"
import { inject, ref } from "vue"
import Message from "../Message.vue"

const emitter = inject("emitter")
const { getStore } = inject("storage")
const adapter = inject("adapter")
const { t } = inject("i18n")

const props = defineProps({
  selection: Object,
  current: Object,
})

const name = ref("")
const message = ref("")

const createFolder = () => {
  if (name.value != "") {
    emitter.emit("vf-fetch", {
      params: {
        q: "newfolder",
        adapter: adapter.value,
        path: props.current.dirname,
        name: name.value,
      },
      onSuccess: () => {
        emitter.emit("vf-toast-push", { label: t("%s is created.", name.value) })
      },
      onError: (e) => {
        message.value = t(e.message)
      },
    })
  }
}
</script>

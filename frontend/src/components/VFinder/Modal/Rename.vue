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
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
          />
        </svg>
      </div>
      <div class="mt-3 w-full text-center sm:ml-4 sm:mt-0 sm:text-left">
        <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-400" id="modal-title">
          {{ t("Rename") }}
        </h3>
        <div class="mt-2">
          <p class="flex py-2 text-sm text-gray-800 dark:text-gray-400">
            <svg
              v-if="item.type == 'dir'"
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 fill-sky-500 stroke-sky-500 text-neutral-500 dark:fill-slate-500 dark:stroke-slate-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 text-neutral-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
              />
            </svg>
            <span class="ml-1.5">{{ item.basename }}</span>
          </p>
          <input
            v-model="name"
            @keyup.enter="rename"
            class="w-full rounded border px-2 py-1 dark:bg-gray-700/25 dark:text-gray-100 dark:focus:border-gray-600 dark:focus:ring-gray-600"
            placeholder="Name"
            type="text"
          />
          <message v-if="message.length" @hidden="message = ''" error>{{ message }}</message>
        </div>
      </div>
    </div>

    <template v-slot:buttons>
      <button
        type="button"
        @click="rename"
        class="inline-flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:bg-gray-700 dark:hover:bg-gray-600/75 sm:ml-3 sm:w-auto sm:text-sm"
      >
        {{ t("Rename") }}
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
  name: "VFModalRename",
}
</script>

<script setup>
import VFModalLayout from "./Layout"
import Message from "../Message"

const emitter = inject("emitter")
const { getStore } = inject("storage")
const adapter = inject("adapter")
const { t } = inject("i18n")

const props = defineProps({
  selection: Object,
  current: Object,
})

const item = ref(props.selection.items[0])
const name = ref(props.selection.items[0].basename)
const message = ref("")

const rename = () => {
  if (name.value != "") {
    emitter.emit("vf-fetch", {
      params: {
        q: "rename",
        adapter: adapter.value,
        path: props.current.dirname,
        item: item.value.path,
        name: name.value,
      },
      onSuccess: () => {
        emitter.emit("vf-toast-push", { label: t("%s is renamed.", name.value) })
      },
      onError: (e) => {
        message.value = t(e.message)
      },
    })
  }
}
</script>

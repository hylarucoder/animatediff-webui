<template>
  <v-f-modal-layout>
    <div class="sm:flex sm:items-start">
      <div
        class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 dark:bg-gray-500 sm:mx-0 sm:h-10 sm:w-10"
      >
        <svg
          class="h-6 w-6 stroke-red-600 dark:stroke-red-200"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <div class="mt-3 w-full text-center sm:ml-4 sm:mt-0 sm:text-left">
        <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-400" id="modal-title">
          {{ t("Move files") }}
        </h3>
        <div class="mt-2">
          <p v-for="node in items" class="flex text-sm text-gray-800 dark:text-gray-400">
            <svg
              v-if="node.type == 'dir'"
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
            <span class="ml-1.5">{{ node.path }}</span>
          </p>
          <p class="pb-1 pt-3 text-sm text-gray-500">{{ t("Are you sure you want to move these files?") }}</p>
          <p class="flex text-sm text-gray-800 dark:text-gray-400">
            <svg
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
            <span class="ml-1.5 overflow-auto">{{ selection.items.to.path }}</span>
          </p>
          <message v-if="message.length" @hidden="message = ''" error>{{ message }}</message>
        </div>
      </div>
    </div>

    <template v-slot:buttons>
      <button
        type="button"
        @click="move"
        class="inline-flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:bg-gray-700 dark:hover:bg-gray-600/75 sm:ml-3 sm:w-auto sm:text-sm"
      >
        {{ t("Yes, Move!") }}
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
  name: "VFModalMove",
}
</script>

<script setup>
import VFModalLayout from "./ModalLayout.vue"
import { inject, ref } from "vue"
import Message from "../Message.vue"

const emitter = inject("emitter")
const { t } = inject("i18n")
const { getStore } = inject("storage")
const adapter = inject("adapter")

const props = defineProps({
  selection: Object,
  current: Object,
})

const items = ref(props.selection.items.from)
const message = ref("")

const move = () => {
  if (items.value.length) {
    emitter.emit("vf-fetch", {
      params: {
        q: "move",
        adapter: adapter.value,
        path: props.current.dirname,
        items: JSON.stringify(items.value.map(({ path, type }) => ({ path, type }))),
        item: props.selection.items.to.path,
      },
      onSuccess: () => {
        emitter.emit("vf-toast-push", { label: t("Files moved.", props.selection.items.to.name) })
      },
      onError: (e) => {
        message.value = t(e.message)
      },
    })
  }
}
</script>

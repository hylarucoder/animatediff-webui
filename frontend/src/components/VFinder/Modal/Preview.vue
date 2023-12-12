<template>
  <v-f-modal-layout>
    <div class="sm:flex sm:items-start">
      <div class="mt-3 w-full text-center sm:mt-0 sm:text-left">
        <div>
          <VFinderPreviewText v-if="loadPreview('text')" :selection="selection" @load="setLoad(true)" />
          <VFinderPreviewImage v-else-if="loadPreview('image')" :selection="selection" @load="setLoad(true)" />
          <VFinderPreviewVideo v-else-if="loadPreview('video')" :selection="selection" @load="setLoad(true)" />
          <VFinderPreviewAudio v-else-if="loadPreview('audio')" :selection="selection" @load="setLoad(true)" />
          <VFinderPreviewPdf v-else-if="loadPreview('application/pdf')" :selection="selection" @load="setLoad(true)" />
          <VFinderPreviewDefault v-else :selection="selection" @load="setLoad(true)" />
        </div>

        <div class="text-sm text-gray-700 dark:text-gray-200">
          <div class="flex leading-5" v-if="loaded == false">
            <svg
              class="-ml-1 mr-3 h-5 w-5 animate-spin text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="stroke-blue-900 opacity-25 dark:stroke-blue-100"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>{{ t("Loading") }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="flex break-all rounded py-2 text-xs font-normal dark:text-gray-200">
      <div>
        <span class="pl-2 font-bold">{{ t("File Size") }}: </span>{{ filesize(selection.item.file_size) }}
      </div>
      <div>
        <span class="pl-2 font-bold">{{ t("Last Modified") }}: </span>
        {{ datetimestring(selection.item.last_modified) }}
      </div>
    </div>

    <template v-slot:buttons>
      <button
        type="button"
        @click="emitter.emit('vf-modal-close')"
        class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-gray-400 sm:ml-3 sm:mt-0 sm:w-auto sm:text-sm"
      >
        {{ t("Close") }}
      </button>
      <button
        type="button"
        @click="download()"
        class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-gray-400 sm:ml-3 sm:mt-0 sm:w-auto sm:text-sm"
      >
        {{ t("Download") }}
      </button>
    </template>
  </v-f-modal-layout>
</template>

<script></script>

<script setup>
import buildURLQuery from "../utils/buildURLQuery"
import { useApiUrl } from "../composables/useApiUrl"
import filesize from "../utils/filesize"
import datetimestring from "../utils/datetimestring"
import VFModalLayout from "./Layout"

const { apiUrl } = useApiUrl()
const emitter = inject("emitter")
const { t } = inject("i18n")
const loaded = ref(false)

const setLoad = (bool) => (loaded.value = bool)

const props = defineProps({
  selection: Object,
})

const loadPreview = (type) => (props.selection.item.mime_type ?? "").startsWith(type)

const download = () => {
  const url =
    apiUrl.value +
    "?" +
    buildURLQuery({
      q: "download",
      adapter: props.selection.adapter,
      path: props.selection.item.path,
    })
  emitter.emit("vf-download", url)
}
</script>

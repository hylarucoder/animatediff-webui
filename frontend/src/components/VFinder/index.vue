<template>
  <div class="vuefinder h-full w-full" :class="darkMode ? 'dark' : ''">
    <div
      :class="fullScreen ? 'fixed inset-0 z-20 w-screen' : 'relative rounded-md'"
      :style="!fullScreen ? 'max-height: ' + maxHeight : ''"
      class="flex min-h-[600px] w-full min-w-min select-none flex-col border border-neutral-300 bg-white text-gray-700 dark:border-gray-900 dark:bg-gray-800 dark:text-neutral-400"
      @mousedown="emitter.emit('vf-contextmenu-hide')"
      @touchstart.passive="emitter.emit('vf-contextmenu-hide')"
    >
      <v-f-toolbar :data="fetchData" />
      <v-f-breadcrumb :data="fetchData" />
      <v-f-explorer :view="view" :data="fetchData" />
      <v-f-statusbar :data="fetchData" />
    </div>

    <template v-if="modal.active">
      <v-finder-modal-preview v-if="'Preview' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-archive v-if="'Archive' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-delete v-if="'Delete' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-message v-if="'Message' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-move v-if="'Move' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-new-file v-if="'NewFile' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-new-folder v-if="'NewFolder' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-rename v-if="'Rename' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-unarchive v-if="'Unarchive' == modal.type" :selection="modal.data" :current="fetchData" />
      <v-finder-modal-upload v-if="'Upload' == modal.type" :selection="modal.data" :current="fetchData" />
    </template>

    <v-f-context-menu :current="fetchData" />
    <iframe id="download_frame" style="display: none" />
  </div>
</template>

<script setup lang="ts">
import mitt from "mitt"
import ajax from "./utils/ajax"
import { useStorage } from "./composables/useStorage"
import { useApiUrl } from "./composables/useApiUrl"
import VFToolbar from "./Toolbar.vue"
import VFExplorer from "./Explorer.vue"
import VFStatusbar from "./Statusbar.vue"
import VFBreadcrumb from "./Breadcrumb.vue"
import VFContextMenu from "./ContextMenu.vue"
import { useI18n } from "./composables/useI18n"

const props = defineProps({
  url: {
    type: [String],
  },
  id: {
    type: String,
    default: "vf",
  },
  dark: {
    type: Boolean,
    default: false,
  },
  usePropDarkMode: {
    type: Boolean,
    default: false,
  },
  locale: {
    type: String,
    default: "en",
  },
  maxHeight: {
    type: String,
    default: "800px",
  },
  maxFileSize: {
    type: String,
    default: "20mb",
  },
  postData: {
    type: Object,
    default: {},
  },
})
const emitter = mitt()
const { setStore, getStore } = useStorage(props.id)
const adapter = ref(getStore("adapter"))

provide("emitter", emitter)
provide("storage", useStorage(props.id))
provide("postData", props.postData)
provide("adapter", adapter)
provide("maxFileSize", props.maxFileSize)
provide("usePropDarkMode", props.usePropDarkMode)

// Lang Management
const i18n = useI18n(props.id, props.locale, emitter)
const { t } = i18n
provide("i18n", i18n)

const { apiUrl, setApiUrl } = useApiUrl()
setApiUrl(props.url)

const fetchData = reactive({
  adapter: adapter.value,
  storages: [],
  dirname: ".",
  files: [],
})

// View Management
const view = ref(getStore("viewport", "grid"))
const darkMode = props.usePropDarkMode ? computed(() => props.dark) : ref(getStore("darkMode", props.dark))

emitter.on("vf-darkMode-toggle", () => {
  darkMode.value = !darkMode.value
  setStore("darkMode", darkMode.value)
})

const loadingState = ref(false)

provide("loadingState", loadingState)

const fullScreen = ref(getStore("full-screen", false))

emitter.on("vf-fullscreen-toggle", () => {
  fullScreen.value = !fullScreen.value
  setStore("full-screen", fullScreen.value)
})

emitter.on("vf-view-toggle", (newView) => {
  view.value = newView
})

// Modal Management
const modal = reactive({
  active: false,
  type: "delete",
  data: {},
})

emitter.on("vf-modal-close", () => {
  modal.active = false
})

emitter.on("vf-modal-show", (item) => {
  modal.active = true
  modal.type = item.type
  modal.data = item
})

const updateItems = (data) => {
  Object.assign(fetchData, data)
  emitter.emit("vf-nodes-selected", {})
  emitter.emit("vf-explorer-update")
}

let controller
emitter.on("vf-fetch-abort", () => {
  controller.abort()
  loadingState.value = false
})

emitter.on("vf-fetch", ({ params, onSuccess = null, onError = null }) => {
  if (["index", "search"].includes(params.q)) {
    if (controller) {
      controller.abort()
    }
    loadingState.value = true
  }

  controller = new AbortController()
  const signal = controller.signal
  ajax(apiUrl.value, {
    params,
    signal,
  })
    .then((data) => {
      adapter.value = data.adapter
      if (["index", "search"].includes(params.q)) {
        loadingState.value = false
      }
      emitter.emit("vf-modal-close")
      updateItems(data)
      onSuccess(data)
    })
    .catch((e) => {
      if (onError) {
        onError(e)
      }
    })
    .finally(() => {})
})

emitter.on("vf-download", (url) => {
  document.getElementById("download_frame").src = url
  emitter.emit("vf-modal-close")
})

onMounted(() => {
  emitter.emit("vf-fetch", {
    params: {
      q: "index",
      adapter: adapter.value,
    },
  })
})
</script>

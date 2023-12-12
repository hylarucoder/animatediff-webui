<template>
  <div
    class="flex select-none items-center border-b border-t border-neutral-300 bg-neutral-100 p-1.5 text-xs dark:border-gray-700/50 dark:bg-gray-800"
  >
    <span :aria-label="t('Go up a directory')" data-microtip-position="bottom-right" role="tooltip">
      <svg
        class="h-6 w-6 rounded p-0.5"
        :class="
          isGoUpAvailable()
            ? 'cursor-pointer text-slate-700 hover:bg-neutral-300 dark:text-neutral-200 dark:hover:bg-gray-700'
            : 'text-gray-400 dark:text-neutral-500'
        "
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
        @dragover="handleDragOver($event)"
        @drop="handleDropZone($event)"
        @click="
          !isGoUpAvailable() ||
            emitter.emit('vf-fetch', {
              params: {
                q: 'index',
                adapter: data.adapter,
                path: breadcrumb[breadcrumb.length - 2]?.path ?? adapter + '://',
              },
            })
        "
      >
        <path
          fill-rule="evenodd"
          d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"
          clip-rule="evenodd"
        />
      </svg>
    </span>
    <span v-if="!isLoading()" :aria-label="t('Refresh')" data-microtip-position="bottom-right" role="tooltip">
      <svg
        class="h-6 w-6 cursor-pointer rounded p-1 text-slate-700 hover:bg-neutral-300 dark:text-neutral-200 dark:hover:bg-gray-700"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="-40 -40 580 580"
        fill="currentColor"
        @click="emitter.emit('vf-fetch', { params: { q: 'index', adapter: data.adapter, path: data.dirname } })"
      >
        <path
          d="M463.5 224H472c13.3 0 24-10.7 24-24V72c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2L413.4 96.6c-87.6-86.5-228.7-86.2-315.8 1c-87.5 87.5-87.5 229.3 0 316.8s229.3 87.5 316.8 0c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0c-62.5 62.5-163.8 62.5-226.3 0s-62.5-163.8 0-226.3c62.2-62.2 162.7-62.5 225.3-1L327 183c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8H463.5z"
        />
      </svg>
    </span>
    <span v-else :aria-label="t('Cancel')" data-microtip-position="bottom-right" role="tooltip">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="h-6 w-6 cursor-pointer rounded p-1 text-slate-700 hover:bg-neutral-300 dark:text-neutral-200 dark:hover:bg-gray-700"
        @click="emitter.emit('vf-fetch-abort')"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </span>

    <div
      v-if="!searchMode"
      class="group ml-2 flex w-full items-center rounded bg-white p-1 dark:bg-gray-700"
      @click.self="enterSearchMode"
    >
      <svg
        class="h-6 w-6 cursor-pointer rounded p-1 text-slate-700 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-gray-800"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
        @click="emitter.emit('vf-fetch', { params: { q: 'index', adapter: data.adapter } })"
      >
        <path
          d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"
        />
      </svg>

      <div class="flex leading-5">
        <div v-for="(item, index) in breadcrumb" :key="index">
          <span class="mx-0.5 text-neutral-300 dark:text-gray-600">/</span>
          <span
            class="cursor-pointer rounded px-1.5 py-1 text-slate-700 hover:bg-neutral-100 dark:text-slate-200 dark:hover:bg-gray-800"
            :title="item.basename"
            @click="emitter.emit('vf-fetch', { params: { q: 'index', adapter: data.adapter, path: item.path } })"
          >{{ item.name }}</span>
        </div>
      </div>

      <svg
        v-if="isLoading()"
        class="ml-auto h-6 w-6 animate-spin p-1 text-white"
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
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
    <div v-else class="relative ml-2 flex w-full items-center rounded bg-white p-1 dark:bg-gray-700">
      <svg
        class="m-auto h-6 w-6 fill-gray-100 stroke-gray-400 p-1 dark:fill-gray-400/20 dark:stroke-gray-400"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
        />
      </svg>
      <div class="w-full" />
      <input
        ref="searchInput"
        v-model="query"
        :placeholder="t('Search anything..')"
        class="absolute ml-4 border-0 bg-transparent px-2 pb-0 pt-1 text-gray-600 outline-0 ring-0 focus:border-transparent focus:ring-transparent dark:text-gray-300 dark:focus:border-transparent dark:focus:ring-transparent"
        type="text"
        @keydown.esc="exitSearchMode"
        @blur="handleBlur"
      >
      <svg
        class="h-6 w-6 cursor-pointer"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        @click="exitSearchMode"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </div>
  </div>
</template>

<script>
</script>

<script setup>
import useDebouncedRef from "./composables/useDebouncedRef"

const emitter = inject("emitter")
const { getStore } = inject("storage")
const adapter = inject("adapter")
const dirname = ref(null)
const breadcrumb = ref([])
const searchMode = ref(false)
const searchInput = ref(null)

const props = defineProps({
  data: Object,
})

const { t } = inject("i18n")
const loadingState = inject("loadingState")

emitter.on("vf-explorer-update", () => {
  const items = []
  let links = []
  dirname.value = props.data.dirname ?? adapter.value + "://"

  if (dirname.value.length == 0) {
    breadcrumb.value = []
  }
  dirname.value
    .replace(adapter.value + "://", "")
    .split("/")
    .forEach(function (item) {
      items.push(item)
      if (items.join("/") != "") {
        links.push({
          basename: item,
          name: item,
          path: adapter.value + "://" + items.join("/"),
          type: "dir",
        })
      }
    })

  if (links.length > 4) {
    links = links.slice(-5)
    links[0].name = ".."
  }

  breadcrumb.value = links
})

const exitSearchMode = () => {
  searchMode.value = false
  query.value = ""
}

emitter.on("vf-search-exit", () => {
  exitSearchMode()
})

const enterSearchMode = () => {
  searchMode.value = true
  nextTick(() => searchInput.value.focus())
}

const query = useDebouncedRef("", 400)

const isLoading = () => loadingState.value

watch(query, (newQuery) => {
  emitter.emit("vf-toast-clear")
  emitter.emit("vf-search-query", { newQuery })
})

const isGoUpAvailable = () => {
  return breadcrumb.value.length && !searchMode.value
}

const handleDropZone = (e) => {
  e.preventDefault()
  const draggedItems = JSON.parse(e.dataTransfer.getData("items"))

  if (draggedItems.find((item) => item.storage != adapter.value)) {
    alert("Moving items between different storages is not supported yet.")
    return
  }

  emitter.emit("vf-modal-show", {
    type: "Move",
    items: { from: draggedItems, to: breadcrumb.value[breadcrumb.value.length - 2] ?? { path: adapter.value + "://" } },
  })
}

const handleDragOver = (e) => {
  e.preventDefault()

  if (isGoUpAvailable()) {
    e.dataTransfer.dropEffect = "copy"
  } else {
    e.dataTransfer.dropEffect = "none"
    e.dataTransfer.effectAllowed = "none"
  }
}

const handleBlur = () => {
  if (query.value == "") {
    exitSearchMode()
  }
}
</script>

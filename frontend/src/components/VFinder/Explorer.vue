<template>
  <div class="relative flex flex-auto flex-col overflow-hidden">
    <div
      v-if="view === 'list' || searchQuery.length"
      class="grid select-none grid-cols-12 border-b border-neutral-300 border-zinc-100 text-xs dark:border-gray-700"
    >
      <div
        class="col-span-7 flex items-center bg-neutral-50 py-1 pl-1 leading-6 hover:bg-neutral-100 dark:bg-gray-800 dark:hover:bg-gray-700/10"
        @click="sortBy('basename')"
      >
        {{ t("Name") }}
        <v-f-sort-icon
          v-show="sort.active && sort.column == 'basename'"
          :direction="sort.order == 'asc' ? 'down' : 'up'"
        />
      </div>
      <div
        v-if="!searchQuery.length"
        class="col-span-2 flex items-center justify-center border-l border-r bg-neutral-50 py-1 leading-6 hover:bg-neutral-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700/10"
        @click="sortBy('file_size')"
      >
        {{ t("Size") }}
        <v-f-sort-icon
          v-show="sort.active && sort.column == 'file_size'"
          :direction="sort.order == 'asc' ? 'down' : 'up'"
        />
      </div>
      <div
        v-if="!searchQuery.length"
        class="col-span-3 flex items-center justify-center bg-neutral-50 py-1 leading-6 hover:bg-neutral-100 dark:bg-gray-800 dark:hover:bg-gray-700/10"
        @click="sortBy('last_modified')"
      >
        {{ t("Date") }}
        <v-f-sort-icon
          v-show="sort.active && sort.column == 'last_modified'"
          :direction="sort.order == 'asc' ? 'down' : 'up'"
        />
      </div>
      <div
        v-if="searchQuery.length"
        class="col-span-5 flex items-center justify-center border-l bg-neutral-50 py-1 leading-6 hover:bg-neutral-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700/10"
        @click="sortBy('path')"
      >
        {{ t("Filepath") }}
        <v-f-sort-icon v-show="sort.active && sort.column == 'path'" :direction="sort.order == 'asc' ? 'down' : 'up'" />
      </div>
    </div>

    <div class="absolute">
      <div ref="dragImage" class="absolute -top-96 -z-50">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="absolute z-10 m-auto h-6 w-6 fill-white stroke-neutral-500 dark:fill-gray-700 dark:stroke-gray-600 md:h-12 md:w-12"
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
        <div
          class="absolute right-[-2rem] top-4 z-20 p-1 text-center text-xs text-neutral-700 dark:text-neutral-300 md:right-[-2.4rem] md:top-5"
        >
          {{ selectedCount }}
        </div>
      </div>
    </div>

    <div
      ref="selectorArea"
      :class="fullScreen ? '' : 'resize-y'"
      class="vf-selector-area z-0 h-full min-h-[150px] w-full overflow-auto p-1 text-xs"
      @touchstart.passive="handleTouchStart"
      @contextmenu.self.prevent="
        emitter.emit('vf-contextmenu-show', { event: $event, area: selectorArea, items: getSelectedItems() })
      "
    >
      <div
        v-for="(item, index) in getItems()"
        v-if="searchQuery.length"
        :class="'vf-item-' + randId"
        class="my-0.5 grid w-full select-none grid-cols-1 border border-transparent hover:bg-neutral-50 dark:hover:bg-gray-700"
        :data-type="item.type"
        :data-item="JSON.stringify(item)"
        :data-index="index"
        @dblclick="openItem(item)"
        @touchstart.passive="delayedOpenItem($event)"
        @touchend="clearTimeOut()"
        @contextmenu.prevent="
          emitter.emit('vf-contextmenu-show', {
            event: $event,
            area: selectorArea,
            items: getSelectedItems(),
            target: item,
          })
        "
      >
        <div class="grid grid-cols-12 items-center">
          <div class="col-span-7 flex items-center">
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
            <span class="overflow-hidden overflow-ellipsis whitespace-nowrap">{{ item.basename }}</span>
          </div>
          <div class="col-span-5 overflow-hidden overflow-ellipsis whitespace-nowrap">
            {{ item.path }}
          </div>
        </div>
      </div>

      <div
        v-for="(item, index) in getItems()"
        v-if="view == 'list' && !searchQuery.length"
        draggable="true"
        :class="'vf-item-' + randId"
        class="my-0.5 grid w-full select-none grid-cols-1 border border-transparent hover:bg-neutral-50 dark:hover:bg-gray-700"
        :data-type="item.type"
        :data-item="JSON.stringify(item)"
        :data-index="index"
        @dblclick="openItem(item)"
        @touchstart.passive="delayedOpenItem($event)"
        @touchend="clearTimeOut()"
        @contextmenu.prevent="
          emitter.emit('vf-contextmenu-show', {
            event: $event,
            area: selectorArea,
            items: getSelectedItems(),
            target: item,
          })
        "
        @dragstart="handleDragStart($event, item)"
        @dragover="handleDragOver($event, item)"
        @drop="handleDropZone($event, item)"
      >
        <div class="grid grid-cols-12 items-center">
          <div class="col-span-7 flex items-center">
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
            <span class="overflow-hidden overflow-ellipsis whitespace-nowrap">{{ item.basename }}</span>
          </div>
          <div class="col-span-2 text-center">
            {{ item.file_size ? filesize(item.file_size) : "" }}
          </div>
          <div class="col-span-3 overflow-hidden overflow-ellipsis whitespace-nowrap">
            {{ datetimestring(item.last_modified) }}
          </div>
        </div>
      </div>

      <div
        v-for="(item, index) in getItems(false)"
        v-if="view == 'grid' && !searchQuery.length"
        draggable="true"
        :class="'vf-item-' + randId"
        class="m-1 inline-flex h-20 w-[5.5rem] select-none justify-center border border-transparent text-center hover:bg-neutral-50 dark:hover:bg-gray-700 md:w-24"
        :data-type="item.type"
        :data-item="JSON.stringify(item)"
        :data-index="index"
        @dblclick="openItem(item)"
        @touchstart.passive="delayedOpenItem($event)"
        @touchend="clearTimeOut()"
        @contextmenu.prevent="
          emitter.emit('vf-contextmenu-show', {
            event: $event,
            area: selectorArea,
            items: getSelectedItems(),
            target: item,
          })
        "
        @dragstart="handleDragStart($event, item)"
        @dragover="handleDragOver($event, item)"
        @drop="handleDropZone($event, item)"
      >
        <div>
          <div class="relative">
            <svg
              v-if="item.type == 'dir'"
              xmlns="http://www.w3.org/2000/svg"
              class="m-auto h-10 w-10 fill-sky-500 stroke-sky-500 dark:fill-slate-500 dark:stroke-slate-500 md:h-12 md:w-12"
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
            <img
              v-else-if="(item.mime_type ?? '').startsWith('image')"
              class="lazy m-auto h-10 md:h-12"
              :data-src="getImageUrl(adapter.value, item.path)"
              :alt="item.basename"
            />
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              class="m-auto h-10 w-10 text-neutral-500 md:h-12 md:w-12"
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
            <div
              v-if="!(item.mime_type ?? '').startsWith('image') && item.type != 'dir'"
              class="absolute top-1/2 hidden w-full text-center text-neutral-500 md:block"
            >
              {{ ext(item.extension) }}
            </div>
          </div>
          <span class="break-all">{{ title_shorten(item.basename) }}</span>
        </div>
      </div>
    </div>
    <v-f-toast />
  </div>
</template>

<script setup lang="ts">
import DragSelect from "dragselect"
import LazyLoad from "vanilla-lazyload"
import datetimestring from "./utils/datetimestring"
import { getImageUrl } from "./utils/getImageUrl"
import filesize from "./utils/filesize"
import VFSortIcon from "./SortIcon.vue"
import VFToast from "./Toast.vue"

const props = defineProps({
  view: String,
  data: Object,
  search: Object,
})

const emitter = inject("emitter")
const { setStore, getStore } = inject("storage")
const adapter = inject("adapter")
const ext = (item) => item?.substring(0, 3)
const title_shorten = (title) => title.replace(/((?=([\w\W]{0,14}))([\w\W]{8,})([\w\W]{8,}))/, "$2..$4")
const selectorArea = ref(null)
const dragImage = ref(null)
const selectedCount = ref(0)
const ds = ref(null)
const { t } = inject("i18n")
const randId = Math.floor(Math.random() * 2 ** 32)
const fullScreen = ref(getStore("full-screen", false))

const vfLazyLoad = new LazyLoad()

emitter.on("vf-fullscreen-toggle", () => {
  selectorArea.value.style.height = null
  fullScreen.value = !fullScreen.value
  setStore("full-screen", fullScreen.value)
})

const searchQuery = ref("")

emitter.on("vf-search-query", ({ newQuery }) => {
  searchQuery.value = newQuery

  if (newQuery) {
    emitter.emit("vf-fetch", {
      params: {
        q: "search",
        adapter: props.data.adapter,
        path: props.data.dirname,
        filter: newQuery,
      },
      onSuccess: (data) => {
        if (!data.files.length) {
          emitter.emit("vf-toast-push", { label: t("No search result found.") })
        }
      },
    })
  } else {
    emitter.emit("vf-fetch", {
      params: {
        q: "index",
        adapter: props.data.adapter,
        path: props.data.dirname,
      },
    })
  }
})

let touchTimeOut = null

const clearTimeOut = () => {
  if (touchTimeOut) {
    clearTimeout(touchTimeOut)
  }
}

// on ios devices scrollbars are hidden as system level.
// to be able to scroll, 2 finger tap needed.
// this is the easiest way that I can think of.
const dragAndDrop = ref(true)
const handleTouchStart = (event) => {
  if (event.touches.length > 1) {
    if (!dragAndDrop.value) {
      ds.value.start()
      emitter.emit("vf-toast-push", { label: t("Drag&Drop: on") })
      emitter.emit("vf-explorer-update")
    } else {
      ds.value.stop()
      emitter.emit("vf-toast-push", { label: t("Drag&Drop: off") })
    }
    dragAndDrop.value = !dragAndDrop.value
  }
}

const delayedOpenItem = ($event) => {
  touchTimeOut = setTimeout(() => {
    const cmEvent = new MouseEvent("contextmenu", {
      bubbles: true,
      cancelable: false,
      view: window,
      button: 2,
      buttons: 0,
      clientX: $event.target.getBoundingClientRect().x,
      clientY: $event.target.getBoundingClientRect().y,
    })
    $event.target.dispatchEvent(cmEvent)
  }, 500)
}

const openItem = (item) => {
  if (item.type === "dir") {
    emitter.emit("vf-search-exit")
    emitter.emit("vf-fetch", {
      params: {
        q: "index",
        adapter: props.data.adapter,
        path: item.path,
      },
    })
  } else {
    emitter.emit("vf-modal-show", {
      type: "Preview",
      adapter: props.data.adapter,
      item,
    })
  }
}

const sort = reactive({
  active: false,
  column: "",
  order: "",
})

const getItems = (sorted = true) => {
  let files = [...props.data.files]
  const column = sort.column
  const order = sort.order == "asc" ? 1 : -1

  if (!sorted) {
    return files
  }

  const compare = (a, b) => {
    if (typeof a === "string" && typeof b === "string") {
      return a.toLowerCase().localeCompare(b.toLowerCase())
    }
    if (a < b) {
      return -1
    }
    if (a > b) {
      return 1
    }
    return 0
  }

  if (sort.active) {
    files = files.slice().sort((a, b) => compare(a[column], b[column]) * order)
  }

  return files
}

const sortBy = (column) => {
  if (sort.active && sort.column == column) {
    sort.active = sort.order == "asc"
    sort.column = column
    sort.order = "desc"
  } else {
    sort.active = true
    sort.column = column
    sort.order = "asc"
  }
}

const getSelectedItems = () => ds.value.getSelection().map((el) => JSON.parse(el.dataset.item))

const handleDragStart = (e, item) => {
  if (e.altKey || e.ctrlKey || e.metaKey) {
    e.preventDefault()
    return false
  }

  e.dataTransfer.setDragImage(dragImage.value, 0, 15)
  e.dataTransfer.effectAllowed = "all"
  e.dataTransfer.dropEffect = "copy"
  e.dataTransfer.setData("items", JSON.stringify(getSelectedItems()))
}

const handleDropZone = (e, item) => {
  e.preventDefault()
  const draggedItems = JSON.parse(e.dataTransfer.getData("items"))

  if (draggedItems.find((item) => item.storage != adapter.value)) {
    alert("Moving items between different storages is not supported yet.")
    return
  }

  emitter.emit("vf-modal-show", {
    type: "Move",
    items: {
      from: draggedItems,
      to: item,
    },
  })
}

const handleDragOver = (e, item) => {
  e.preventDefault()
  if (!item || item.type !== "dir" || ds.value.getSelection().find((el) => el == e.currentTarget)) {
    e.dataTransfer.dropEffect = "none"
    e.dataTransfer.effectAllowed = "none"
  } else {
    e.dataTransfer.dropEffect = "copy"
  }
}

const setDragSelect = () => {
  ds.value = new DragSelect({
    area: selectorArea.value,
    keyboardDrag: false,
    selectedClass: "vf-explorer-selected",
    selectorClass: "vf-explorer-selector",
  })

  emitter.on("vf-explorer-update", () =>
    nextTick(() => {
      ds.value.clearSelection()
      ds.value.setSelectables(document.getElementsByClassName("vf-item-" + randId))
    }),
  )

  ds.value.subscribe("predragstart", ({ event, isDragging }) => {
    // apply custom drag event
    if (isDragging) {
      selectedCount.value = ds.value.getSelection().length
      ds.value.break()
    } else {
      // if resizing selectable area at the corner dont start selection.
      const offsetX = event.target.offsetWidth - event.offsetX
      const offsetY = event.target.offsetHeight - event.offsetY
      if (offsetX < 15 && offsetY < 15) {
        ds.value.clearSelection()
        ds.value.break()
      }
    }
  })

  ds.value.subscribe("predragmove", ({ isDragging }) => {
    if (isDragging) {
      ds.value.break()
    }
  })

  ds.value.subscribe("callback", ({ items, event, isDragging }) => {
    emitter.emit("vf-nodes-selected", getSelectedItems())
    selectedCount.value = ds.value.getSelection().length
  })
}

onMounted(setDragSelect)

onUpdated(() => {
  ds.value.Area.reset()
  ds.value.SelectorArea.updatePos()
  vfLazyLoad.update()
})

onMounted(() => {
  watch(
    () => props.view,
    () => emitter.emit("vf-explorer-update"),
  )
})
</script>

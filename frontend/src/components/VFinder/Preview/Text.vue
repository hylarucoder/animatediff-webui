<template>
  <div class="flex">
    <div
      class="mb-2 text-lg font-medium leading-6 text-gray-900 dark:text-gray-400"
      id="modal-title"
      :aria-label="selection.item.path"
      data-microtip-position="bottom-right"
      role="tooltip"
    >
      {{ selection.item.basename }}
    </div>
    <div class="mb-2 ml-auto">
      <button
        @click="save"
        class="ml-1 rounded border border-transparent bg-blue-700/75 px-2 py-1 text-base font-medium text-white shadow-sm hover:bg-blue-700 dark:bg-gray-700 dark:hover:bg-gray-700/50 sm:ml-3 sm:w-auto sm:text-sm"
        v-if="showEdit"
      >
        {{ t("Save") }}
      </button>
      <button class="ml-1 px-2 py-1 text-blue-500" @click="editMode()">{{ showEdit ? t("Cancel") : t("Edit") }}</button>
    </div>
  </div>
  <div>
    <pre
      v-if="!showEdit"
      class="max-h-[60vh] min-h-[200px] overflow-auto whitespace-pre-wrap rounded border border-gray-200 p-2 text-xs font-normal dark:border-gray-700/50 dark:text-gray-200"
      >{{ content }}</pre
    >
    <div v-else>
      <textarea
        ref="editInput"
        v-model="contentTemp"
        class="max-h-[60vh] min-h-[200px] w-full rounded p-2 text-xs dark:bg-gray-700 dark:text-gray-200 dark:selection:bg-gray-500 dark:focus:border-gray-600 dark:focus:ring-gray-600"
        name="text"
        id=""
        cols="30"
        rows="10"
      ></textarea>
    </div>
    <v-finder-message v-if="message.length" @hidden="message = ''" :error="isError">{{ message }}</v-finder-message>
  </div>
</template>

<script setup lang="ts">
import ajax from "../utils/ajax"

const emit = defineEmits(["load"])
const content = ref("")
const contentTemp = ref("")
const editInput = ref(null)
const showEdit = ref(false)
const { apiUrl } = useApiUrl()
const props = defineProps({
  selection: Object,
})
const message = ref("")
const isError = ref(false)

const { t } = inject("i18n")

onMounted(() => {
  ajax(apiUrl.value, {
    params: {
      q: "preview",
      adapter: props.selection.adapter,
      path: props.selection.item.path,
    },
    json: false,
  }).then((data) => {
    content.value = data
    emit("load")
  })
})

const editMode = () => {
  showEdit.value = !showEdit.value
  contentTemp.value = content.value
  if (showEdit.value == true) {
    nextTick(() => {
      editInput.value.focus()
    })
  }
}

const postData = inject("postData")

const save = () => {
  message.value = ""
  isError.value = false

  ajax(apiUrl.value, {
    method: "POST",
    params: Object.assign(postData, {
      q: "save",
      adapter: props.selection.adapter,
      path: props.selection.item.path,
      content: contentTemp.value,
    }),
    json: false,
  })
    .then((data) => {
      message.value = t("Updated.")
      content.value = data
      emit("load")
      showEdit.value = !showEdit.value
    })
    .catch((e) => {
      message.value = t(e.message)
      isError.value = true
    })
}
</script>

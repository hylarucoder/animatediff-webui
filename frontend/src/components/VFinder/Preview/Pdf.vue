<template>
  <h3
    id="modal-title"
    class="mb-2 text-lg font-medium leading-6 text-gray-900 dark:text-gray-400"
    :aria-label="selection.item.path"
    data-microtip-position="bottom-right"
    role="tooltip"
  >
    {{ selection.item.basename }}
  </h3>
  <div>
    <object class="h-[60vh]" :data="getPDFUrl()" type="application/pdf" width="100%" height="100%">
      <iframe class="border-0" :src="getPDFUrl()" width="100%" height="100%">
        <p>
          Your browser does not support PDFs.
          <a href="https://example.com/test.pdf">Download the PDF</a>
          .
        </p>
      </iframe>
    </object>
  </div>
</template>

<script setup lang="ts">
import buildURLQuery from "../utils/buildURLQuery"

const { apiUrl } = useApiUrl()
const props = defineProps({
  selection: Object,
})

const emit = defineEmits(["load"])

const getPDFUrl = () => {
  return (
    apiUrl.value +
    "?" +
    buildURLQuery({
      q: "preview",
      adapter: props.selection.adapter,
      path: props.selection.item.path,
    })
  )
}

onMounted(() => {
  emit("load")
})
</script>

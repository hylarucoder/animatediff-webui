<script setup lang="ts">
import { useOptionsStore } from "~/composables/options"
import { useActiveBlockStore } from "~/composables/block"

enum TLoadingEnum {
  PENDING = "PENDING",
  SUCCESS = "SUCCESS",
  FAILED = "FAILED",
}

const loading = ref<TLoadingEnum>(TLoadingEnum.PENDING)

const optionsStore = useOptionsStore()
const activeBlock = useActiveBlockStore()

function retry() {
  return optionsStore
    .init()
    .then(() => {
      loading.value = TLoadingEnum.SUCCESS
    })
    .catch(() => {
      loading.value = TLoadingEnum.FAILED
    })
}

retry()

const btnLoading = ref(false)
const onClickRetry = () => {
  btnLoading.value = true
  retry().finally(() => {
    btnLoading.value = false
  })
}

const cleanBlock = useThrottleFn(() => {
  console.log("Clicked outside of .timetrack-block and .timetrack-block-editor")
  activeBlock.deleteBlock()
}, 1000)

document.addEventListener("click", function (event) {
  const isClickInsideElement =
    event?.target?.closest(".timeline-track-block") || event?.target?.closest(".timeline-track-block-editor")

  if (!isClickInsideElement) {
    cleanBlock()
  }
})
</script>
<template>
  <div v-if="loading === TLoadingEnum.PENDING" class="flex h-screen w-full items-center justify-center p-0 px-0">
    <a-spin tip="Loading..." size="large" />
  </div>
  <div v-else-if="loading === TLoadingEnum.FAILED" class="flex h-screen w-full items-center justify-center p-0 px-0">
    <a-result status="error" title="Loading Failed" sub-title="Please check your network">
      <template #extra>
        <a-button key="retry" :loading="btnLoading" @click="onClickRetry">Try Again</a-button>
      </template>
    </a-result>
  </div>
  <div v-else class="h-screen w-full p-0 px-0">
    <VMenubar class="border-1" />
    <div class="border-x-1 border-b-1 flex h-[--workspace-height] justify-between">
      <VMainPlayer />
      <VRightSidebar />
    </div>
    <VTimelineWindow />
  </div>
</template>

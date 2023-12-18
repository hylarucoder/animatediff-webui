<script lang="ts" setup>
import { useVideoExportStore } from "~/composables/videoExport"
import VProgressMini from "~/components/VProgressMini.vue"

const storeVideoExport = useVideoExportStore()
const { task, isActive } = storeToRefs(storeVideoExport)
const optionsStore = useOptionsStore()
const { optPerformances } = optionsStore
const formStore = useFormStore()
const { sizeOpts, size, duration, performance } = storeToRefs(formStore)

const emit = defineEmits<{
  (e: "closeModal"): void
}>()
const refSubtasks = ref<HTMLElement | null>(null)
watch(
  task,
  () => {
    nextTick(() => {
      if (refSubtasks?.value.length) {
        refSubtasks?.value[refSubtasks.value.length - 1].scrollIntoView({ behavior: "smooth" })
      }
    })
  },
  {
    deep: true,
  },
)
</script>
<template>
  <a-modal centered :open="true" title="Export" @close="emit('closeModal')">
    <div class="flex h-[400px] w-[500px] select-none">
      <div class="flex w-1/2 flex-col pr-5 pt-2 drop-shadow">
        <div class="flex h-full w-full flex-col items-center justify-center bg-zinc-200 px-5">
          <a-progress type="circle" :percent="task.completed" status="active" />
        </div>
        <div ref="refStatusBar" class="h-[100px] overflow-y-scroll bg-zinc-100 p-4">
          <template>
            <div
              v-for="sub in task.subtasks"
              :key="sub.description"
              ref="refSubtasks"
              class="flex flex-col py-0 font-mono"
            >
              <VProgressMini :completed="sub.completed" :description="sub.description" />
              <span>{{ sub.completed }}</span>
            </div>
          </template>
        </div>
      </div>
      <div class="flex w-1/2">
        <a-form layout="vertical">
          <a-form-item label="Performance" required>
            <a-radio-group v-model:value="performance">
              <a-radio v-for="opt in optPerformances" :key="opt.value" :value="opt.value" :label="opt.label">
                {{ opt.label }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="Duration(s)" required>
            <a-input-number v-model:value="duration" class="text-left" />
          </a-form-item>
          <a-form-item label="Output Size" required>
            <a-radio-group v-model:value="size">
              <a-radio v-for="opt in sizeOpts" :key="opt.value" :value="opt.value" :label="opt.label">
                {{ opt.label }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
        </a-form>
      </div>
    </div>
    <template #footer>
      <a-button key="back" @click="emit('closeModal')"> Return</a-button>
      <a-button key="submit" type="primary" :loading="isActive" @click="storeVideoExport.submitExport()">
        Export
      </a-button>
    </template>
  </a-modal>
</template>

<script setup lang="ts">
import { useActiveBlockStore } from "~/composables/block"

const activeBlock = useActiveBlockStore()
const { block, refInput } = storeToRefs(activeBlock)
const { onFocus, onBlur } = activeBlock
</script>
<template>
  <div class="timeline-track-block-editor min-h-full w-full p-5">
    <div v-if="!block">error</div>

    <div v-if="block">
      <a-form layout="vertical">
        <a-form-item label="Time"> {{ block.start / 1000 }}s</a-form-item>
        <a-form-item label="Prompt">
          <v-prompt-input ref="refInput" @focus="onFocus" @blur="onBlur" auto-focus v-model:value="block.prompt" />
        </a-form-item>
        <a-button @click.prevent="activeBlock.deleteBlock()">Save</a-button>
      </a-form>
    </div>
  </div>
</template>

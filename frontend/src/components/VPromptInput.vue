<script setup lang="ts">
const props = defineProps({
  value: {
    type: String,
    default: "",
  },
  autoFocus: {
    type: Boolean,
    default: false,
  },
})
const emit = defineEmits(["update:value"])
const ensureSpaceAfterComma = (text) => {
  // let newText = text.replace(/,\s*/g, ",")
  // newText = newText.replace(/,/g, ", ")
  return text
}
const value = computed({
  get: () => ensureSpaceAfterComma(props.value),
  set: (newValue) => emit("update:value", newValue),
})

const addWeight = (event: KeyboardEvent) => {
  console.log("value", value.value)
  const cursorPosition = (event.target as HTMLTextAreaElement).selectionStart
  const newVal = calculateWeightPrompt(value.value, cursorPosition, true)
  emit("update:value", newVal)
  const target = event.target
  nextTick(() => {
    target.selectionStart = cursorPosition
    target.selectionEnd = cursorPosition
  })
}

const subWeight = (event: KeyboardEvent) => {
  const cursorPosition = (event.target as HTMLTextAreaElement).selectionStart
  const newVal = calculateWeightPrompt(value.value, cursorPosition, false)
  emit("update:value", newVal)
  const target = event.target
  nextTick(() => {
    target.selectionStart = cursorPosition
    target.selectionEnd = cursorPosition
  })
}

const calculateWeightPrompt = (text, cursorPosition, isAdd) => {
  // 找到光标所在的词
  const words = text.match(/(\(.*?\)|[^,]+)/g).map((word) => word.trim())
  let cursorWordIndex = null
  let start = 0

  for (let i = 0; i < words.length; i++) {
    const word = words[i]
    if (start <= cursorPosition && cursorPosition <= start + word.length) {
      cursorWordIndex = i
      break
    }
    start += word.length + 2 // 加上一个分隔符的长度和两侧的空格
  }

  // 对光标所在的词加权、减权或移除权重
  if (cursorWordIndex !== null) {
    let word = words[cursorWordIndex]

    // 检查 word 是否具有权重
    const hasWeight = word.startsWith("(") && word.endsWith(")")
    if (hasWeight) {
      // 解析权重
      const wordBase = word.slice(1, word.lastIndexOf(":"))
      let weight = parseFloat(word.slice(word.lastIndexOf(":") + 1, -1))

      // 加权或减权
      if (isAdd && weight < 1.5) {
        weight = Math.min(weight + 0.1, 1.5)
      } else if (!isAdd && weight > 0.5) {
        weight = Math.max(weight - 0.1, 0.5)
      }

      // 更新 word
      word = `(${wordBase}:${weight.toFixed(1)})`
    } else if (isAdd) {
      // 加权
      word = `(${word}:1.1)`
    } else {
      // 减权
      word = `(${word}:0.9)`
    }

    // 将更新后的词重新插入到文本中
    words[cursorWordIndex] = word
    return words.join(", ")
  }
  return text
}
const inputRef = ref(null)

onMounted(() => {
  if (props.autoFocus) {
    inputRef.value.focus()
  }
})
</script>
<template>
  <a-textarea
    ref="inputRef"
    v-model:value="value"
    :rows="3"
    @keydown.shift.up.prevent="addWeight"
    @keydown.shift.down.prevent="subWeight"
  />
  <!--  <div class="ant-form-item-control-input">-->
  <!--    <div class="ant-form-item-control-input-content">-->
  <!--      <div class="ant-input textarea-like rounded px-2 text-sm" contenteditable="true">-->
  <!--        This is some-->
  <!--        <mark>highlighted</mark>-->
  <!--        text.-->
  <!--      </div>-->
  <!--    </div>-->
  <!--  </div>-->
</template>

<style>
.textarea-like {
  border: 1px solid #ccc;
  font-family: monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 5px;
  overflow: auto;
  width: 100%;
  height: 100px;
}
</style>

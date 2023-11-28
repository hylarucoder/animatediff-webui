<template>
  <ClientOnly>
    <div class="w-full overflow-auto" :class="!isShort ? 'aspect-16/9' : 'aspect-9/16'">
      <lite-youtube
        :videoid="vid"
        class="border-0"
        :short="isShort"
        :width="!isShort ? width : height"
        :height="!isShort ? height : width"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
      />
    </div>
  </ClientOnly>
</template>

<script lang="ts" setup>
const props = defineProps({
  // TODO: responsive
  width: {
    type: Number,
    default: 560 * 2 * 0.6,
  },
  height: {
    type: Number,
    default: 315 * 2 * 0.6,
  },
  isShort: {
    type: Boolean,
    default: false,
  },
  src: {
    type: String,
    required: true,
  },
})

const parseAndReturnEmbed = (url: string) => {
  const isShort = url.startsWith("https://www.youtube.com/shorts/")
  if (isShort) {
    const vid = url.replace("https://www.youtube.com/shorts/", "")
    return {
      vid,
      isShort: true,
      url: "https://www.youtube.com/embed/" + vid,
    }
  } else {
    const vid = new URL(url).searchParams.get("v")
    return {
      vid,
      isShort: false,
      url: "https://www.youtube.com/embed/" + vid,
    }
  }
}

const { isShort, vid } = parseAndReturnEmbed(props.src)
</script>

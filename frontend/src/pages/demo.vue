<template>
  <ClientOnly>
    <div>
      <canvas ref="filmstripCanvas" :width="canvasWidth" :height="canvasHeight"></canvas>
    </div>
  </ClientOnly>
</template>

<script setup lang="ts">

const images = ref<string[]>([
  "https://07akioni.oss-cn-beijing.aliyuncs.com/07akioni.jpeg",
]);
const canvasWidth = ref<number>(800);
const canvasHeight = ref<number>(200);

// Data
const loadedImages = ref<HTMLImageElement[]>([]);
const loadedCount = ref<number>(0);


// Methods
const loadImages = () => {
  for (let i = 0; i < images.value.length; i++) {
    let img = new Image();
    img.onload = () => {
      loadedCount.value++;
      if (loadedCount.value === images.value.length) {
        drawFilmstrip();
      }
    };
    img.src = images.value[i];
    loadedImages.value.push(img);
  }
};

const drawFilmstrip = () => {
  const canvas = filmstripCanvas.value;
  const ctx = canvas.getContext('2d');

  // Calculate image width based on canvas width and number of images
  const imageWidth = canvas.width / loadedImages.value.length;

  // Loop through images and draw each one on the canvas
  for (let i = 0; i < loadedImages.value.length; i++) {
    ctx.drawImage(loadedImages.value[i], i * imageWidth, 0, imageWidth, canvas.height);
  }
};

// Watch for changes in the images prop
watch(images, () => {
  loadedImages.value = [];
  loadedCount.value = 0;
  loadImages();
}, {immediate: true});
// Refs
const filmstripCanvas = ref<HTMLCanvasElement>();
</script>

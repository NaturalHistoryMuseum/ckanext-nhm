<template>
  <div id="osdViewer" :class="$style.viewer"></div>
</template>

<script setup>
import { onMounted, ref, watchEffect } from 'vue';
import OpenSeadragon from 'openseadragon';
import axios from 'axios';
import { useStore } from '../store/main';

const viewer = ref();
const store = useStore();

onMounted(() => {
  viewer.value = OpenSeadragon({
    id: 'osdViewer',
    prefixUrl:
      'https://cdn.jsdelivr.net/gh/Benomrans/openseadragon-icons@main/images/',
    sequenceMode: false,
    showRotationControl: true,
    tileSources: [],
    defaultZoomLevel: 0.8,
    minZoomLevel: 0.2,
  });
});

watchEffect(() => {
  if (store.currentImage == null) {
    return;
  }
  axios.get(store.currentImage.info).then((response) => {
    viewer.value.open(response.data);
  });
});
</script>

<style module lang="scss">
.viewer {
  height: 100%;
  width: 100%;
  border: 2px solid #9a9a9a;
  background-color: black;
}
</style>

<template>
  <div class="container">
    <h1>Image viewer</h1>
    <Overlay />
    <router-view />
  </div>
</template>

<script setup>
import Overlay from './components/Overlay.vue';
import { useStore } from './store';
import { onMounted } from 'vue';

const store = useStore();

onMounted(store.getAllResources);
</script>

<style></style>

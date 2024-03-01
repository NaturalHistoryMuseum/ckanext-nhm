<template>
  <div class="container">
    <h1>Image viewer</h1>
    <Overlay />
    <router-view />
  </div>
</template>

<script setup>
import Overlay from './components/Overlay.vue';
import { useStore } from './store/main';

const store = useStore();
</script>

<style></style>

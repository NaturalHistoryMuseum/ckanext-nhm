<template>
  <div :class="$style.main">
    <div :class="$style.body">
      <slot>
        {{ model }}
      </slot>
    </div>
    <div v-if="isSupported">
      <zoa-button size="sm" @click="copy(model)">
        <i class="fas" :class="copied ? 'fa-check' : 'fa-clipboard'" />
      </zoa-button>
    </div>
  </div>
</template>

<script setup>
import { useClipboard } from '@vueuse/core';
import { ZoaButton } from '@nhm-data/zoa';

const model = defineModel();

const { text, copy, copied, isSupported } = useClipboard({
  model,
  legacy: true,
});
</script>

<style module lang="scss">
.main {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1em;
  align-items: center;
  padding: 5px 10px;
}

.button {
  cursor: pointer;
}
</style>

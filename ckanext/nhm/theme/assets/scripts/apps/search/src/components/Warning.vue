<template>
  <div
    class="flex-container flex-center flex-column alert-warning search-flash"
  >
    <slot>
      <span>{{ message }}</span>
    </slot>
  </div>
</template>

<script>
export default {
  name: 'Warning',
  props: ['message'],
};
</script>

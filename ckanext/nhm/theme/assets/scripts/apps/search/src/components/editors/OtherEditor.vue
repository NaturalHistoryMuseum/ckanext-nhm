<template>
  <div class="flex-container flex-center"></div>
</template>

<script>
import BaseEditor from './BaseEditor.vue';

export default {
  extends: BaseEditor,
  name: 'OtherEditor',
  data: function () {
    return {
      values: {},
    };
  },
};
</script>

<template>
  <div class="flex-container flex-center">
    <span class="fields"> field </span>
    <label for="queryValueText">
      <i
        :class="[
          'fas',
          comparisonType === 'equals' ? 'fa-equals' : 'fa-search',
        ]"
      ></i>
    </label>
    <input
      type="text"
      v-model="values[comparisonType].value"
      id="queryValueText"
      size="10"
      @keyup.enter="pressedEnter"
    />
  </div>
</template>

<script>
import BaseEditor from './BaseEditor.vue';

export default {
  extends: BaseEditor,
  name: 'TextEditor',
  data: function () {
    return {
      values: {
        equals: {
          value: null,
        },
        contains: {
          value: null,
        },
      },
    };
  },
};
</script>

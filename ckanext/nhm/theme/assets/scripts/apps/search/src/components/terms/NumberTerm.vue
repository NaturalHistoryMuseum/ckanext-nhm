<template>
  <div class="filter-term filter-term-number">
    <span v-if="showName" class="filter-term-name">{{
      data.display.name
    }}</span>
    <div class="flex-container" v-if="!showName">
      <span v-if="isRange && data.content.greater_than !== undefined">{{
        data.content.greater_than
      }}</span>
      <span v-if="isRange && data.content.greater_than !== undefined">{{
        data.content.greater_than_inclusive ? '≤' : '<'
      }}</span>
      <FieldsDropdown v-bind:fields="data.content.fields"></FieldsDropdown>
      <span v-if="isRange && data.content.less_than !== undefined">{{
        data.content.less_than_inclusive ? '≤' : '<'
      }}</span>
      <span v-if="isRange && data.content.less_than !== undefined">{{
        data.content.less_than
      }}</span>
      <span v-if="!isRange">{{ comparison === 'contains' ? '~' : '=' }}</span>
      <span v-if="!isRange">{{ data.content.value }}</span>
    </div>
  </div>
</template>

<script>
import BaseTerm from './BaseTerm.vue';

export default {
  extends: BaseTerm,
  name: 'NumberTerm',
  computed: {
    isRange() {
      return this.comparison === 'range';
    },
  },
};
</script>

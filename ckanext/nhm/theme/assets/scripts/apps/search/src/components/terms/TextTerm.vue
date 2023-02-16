<template>
  <div class="filter-term filter-term-text">
    <span v-if="showName" class="filter-term-name">{{
      data.display.name
    }}</span>
    <div class="flex-container" v-if="!showName">
      <FieldsDropdown v-bind:fields="data.content.fields"></FieldsDropdown>
      <span>{{ comparison === 'contains' ? '~' : '=' }}</span>
      <span>{{ data.content.value }}</span>
    </div>
  </div>
</template>

<script>
import BaseTerm from './BaseTerm.vue';

export default {
  extends: BaseTerm,
  name: 'TextTerm',
};
</script>

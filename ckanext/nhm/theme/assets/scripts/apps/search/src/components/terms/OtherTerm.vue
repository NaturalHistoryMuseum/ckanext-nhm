<template>
  <div class="filter-term filter-term-other">
    <span v-if="showName" class="filter-term-name">{{
      data.display.name
    }}</span>
    <div class="flex-container" v-if="!showName">
      <FieldsDropdown v-bind:fields="data.content.fields"></FieldsDropdown>
      <span>{{ comparison }}</span>
    </div>
  </div>
</template>

<script>
import BaseTerm from './BaseTerm.vue';

export default {
  extends: BaseTerm,
  name: 'OtherTerm',
};
</script>

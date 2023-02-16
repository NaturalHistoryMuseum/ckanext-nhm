<template>
  <div :class="[...filterClasses, 'filter-term']">
    <component
      :is="termType"
      v-bind:data="filterItem"
      v-bind:comparison="termComparison"
    ></component>
    <transition name="slideright">
      <TermEditor
        v-if="showEditor"
        :existing-term-id="filterId"
        :parent-id="filterItem.parent"
        v-dismiss="{
          switch: 'showEditor',
          ignore: ['#show-editor-' + _uid, '.delete-field'],
        }"
      ></TermEditor>
    </transition>
    <div class="filter-buttons">
      <i
        class="edit-filter fas fa-pencil-alt fa-xs"
        @click="showEditor = !showEditor"
        :id="'show-editor-' + _uid"
      ></i>
      <i
        class="delete-filter fas fa-times fa-xs"
        @click="deleteSelf"
        v-if="filterItem.parent !== null"
      ></i>
    </div>
  </div>
</template>

<script>
import FilterBase from './FilterBase.vue';
import Loading from './Loading.vue';
import LoadError from './LoadError.vue';
import TextTerm from './terms/TextTerm.vue';
import NumberTerm from './terms/NumberTerm.vue';
import GeoTerm from './terms/GeoTerm.vue';
import OtherTerm from './terms/OtherTerm.vue';

const TermEditor = import('./TermEditor.vue');

export default {
  extends: FilterBase,
  name: 'FilterTerm',
  components: {
    TermEditor: () => ({
      component: TermEditor,
      loading: Loading,
      error: LoadError,
    }),
    string: TextTerm,
    number: NumberTerm,
    geo: GeoTerm,
    other: OtherTerm,
  },
  data: function () {
    return {
      showEditor: false,
    };
  },
  computed: {
    termData() {
      return this.filterItem.content;
    },
    termType() {
      if (!this.filterKey.includes('_')) {
        return 'other';
      } else {
        return this.filterKey.split('_')[0];
      }
    },
    termComparison() {
      return this.filterKey.slice(this.filterKey.indexOf('_') + 1);
    },
  },
};
</script>

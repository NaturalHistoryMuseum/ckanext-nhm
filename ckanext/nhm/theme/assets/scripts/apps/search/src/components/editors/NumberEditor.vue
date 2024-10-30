<template>
  <div class="flex-container flex-center">
    <span v-if="comparisonType === 'range'">
      <input
        type="number"
        v-model="values.range.greater_than"
        @keyup.enter="pressedEnter"
      />
      <input
        type="checkbox"
        v-model="values.range.greater_than_inclusive"
        id="greaterThanEq"
      />
      <label for="greaterThanEq" v-if="comparisonType === 'range'">
        <i
          :class="[
            'fas',
            'fa-less-than' +
              (values.range.greater_than_inclusive ? '-equal' : ''),
          ]"
        ></i>
      </label>
    </span>
    <span class="fields"> field </span>
    <span v-if="comparisonType === 'range'">
      <input
        type="checkbox"
        v-model="values.range.less_than_inclusive"
        id="lessThanEq"
      />
      <label for="lessThanEq">
        <i
          :class="[
            'fas',
            'fa-less-than' + (values.range.less_than_inclusive ? '-equal' : ''),
          ]"
        ></i>
      </label>
      <input
        type="number"
        v-model="values.range.less_than"
        @keyup.enter="pressedEnter"
      />
    </span>
    <span v-if="comparisonType === 'equals'">
      <label for="queryValueInt1"><i class="fas fa-equals"></i></label>
      <input
        type="number"
        v-if="comparisonType === 'equals'"
        v-model="values.equals.value"
        id="queryValueInt1"
        @keyup.enter="pressedEnter"
      />
    </span>
  </div>
</template>

<script>
import BaseEditor from './BaseEditor.vue';
import * as d3 from 'd3-collection';

export default {
  extends: BaseEditor,
  name: 'NumberEditor',
  data: function () {
    return {
      values: {
        equals: {
          value: null,
        },
        range: {
          greater_than: null,
          less_than: null,
          greater_than_inclusive: null,
          less_than_inclusive: null,
        },
      },
    };
  },
  computed: {
    queryValues() {
      d3.keys(this.values[this.comparisonType]).forEach((k) => {
        let v = this.values[this.comparisonType][k];
        if (
          ['value', 'less_than', 'greater_than'].includes(k) &&
          this.values[this.comparisonType][k] !== null
        ) {
          this.$set(this.values[this.comparisonType], k, Number(v));
        }
      });
      return this.values[this.comparisonType];
    },
  },
};
</script>

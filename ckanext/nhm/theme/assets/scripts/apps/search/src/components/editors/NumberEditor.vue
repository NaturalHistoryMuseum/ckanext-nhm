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
          greater_than_inclusive: true,
          less_than_inclusive: true,
        },
      },
      defaults: {
        range: {
          greater_than_inclusive: true,
          less_than_inclusive: true,
        },
      },
    };
  },
  computed: {
    queryValues() {
      // ensure these fields are numbers
      const numberFields = {
        equals: ['value'],
        range: ['greater_than', 'less_than'],
      };
      numberFields[this.comparisonType].forEach((f) => {
        let v = this.values[this.comparisonType][f];
        if (v != null) {
          this.$set(this.values[this.comparisonType], f, Number(v));
        }
      });

      // copy to secondary object, filtering out nulls
      let query = Object.fromEntries(
        Object.entries(this.values[this.comparisonType]).filter(
          (e) => e != null,
        ),
      );

      // remove any unnecessary fields that aren't nulls
      if (this.comparisonType === 'range') {
        if (query.greater_than == null) {
          delete query.greater_than_inclusive;
        }
        if (query.less_than == null) {
          delete query.less_than_inclusive;
        }
      }

      return query;
    },
  },
};
</script>

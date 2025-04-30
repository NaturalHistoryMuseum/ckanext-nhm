<template>
  <div></div>
</template>

<script>
import { mapGetters } from 'vuex';
import * as d3 from 'd3-collection';

export default {
  name: 'BaseEditor',
  props: ['comparisonType', 'existingTermId'],
  data: function () {
    return {
      values: {
        // different comparison types and query entries go here
      },
      defaults: {
        // non-null defaults go here, in the same format as values
      },
    };
  },
  computed: {
    ...mapGetters('results/query/filters', ['getFilterById']),
    queryValues() {
      return this.values[this.comparisonType];
    },
  },
  created: function () {
    this.loadExisting();
  },
  methods: {
    loadExisting() {
      if (this.existingTermId === undefined) {
        return;
      }
      let existing = this.getFilterById(this.existingTermId);

      d3.keys(this.values[this.comparisonType]).forEach((k) => {
        let existingValue = existing.content[k];
        let { [k]: defaultValue = null } =
          this.defaults[this.comparisonType] || {};
        let setDefault = existingValue == null;
        this.$set(
          this.values[this.comparisonType],
          k,
          setDefault ? defaultValue : existingValue,
        );
      });
    },
    pressedEnter() {
      this.$emit('pressed-enter');
    },
  },
  watch: {
    values: {
      handler: function () {
        this.$emit('set-query-values', this.queryValues);
      },
      deep: true,
    },
  },
};
</script>

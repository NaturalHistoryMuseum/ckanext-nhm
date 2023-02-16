<template>
  <div :class="filterClasses"></div>
</template>

<script>
import { mapState, mapGetters, mapMutations } from 'vuex';

export default {
  data: function () {
    return {
      filterClasses: [
        'filter-item',
        'flex-container',
        'flex-stretch-last',
        'flex-right',
        'flex-wrap',
      ],
    };
  },
  props: ['filterId'],
  computed: {
    ...mapState(['schema']),
    ...mapGetters('results/query/filters', ['getFilterById', 'getNestLevel']),
    filterItem() {
      return this.getFilterById(this.filterId);
    },
    filterKey() {
      return this.filterItem.key;
    },
    nestLevel() {
      return this.getNestLevel(this.filterId);
    },
  },
  methods: {
    ...mapMutations('results/query/filters', ['deleteFilter']),
    deleteSelf() {
      this.deleteFilter(this.filterId);
    },
  },
};
</script>

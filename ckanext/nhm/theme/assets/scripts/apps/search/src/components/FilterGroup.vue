<template>
  <div
    :class="[
      ...filterClasses,
      showGroup ? 'filter-group' : 'filter-group-root',
      'filter-type-' + filterKey,
    ]"
  >
    <a
      class="group-type"
      href="javascript:void(0);"
      @click.self="changeGroupType"
      v-if="showGroup"
    >
      {{ readableGroupType }}
    </a>
    <FilterGroup
      v-for="id in subGroups"
      v-bind:filter-id="id"
      v-bind:key="id.id"
    ></FilterGroup>
    <FilterTerm
      v-for="id in subTerms"
      v-bind:filter-id="id"
      v-bind:key="id.id"
      v-if="!getFilterById(id).display.hidden"
    ></FilterTerm>
    <FilterAdd
      v-bind:parent-id="filterId"
      v-bind:key="_uid + '-new'"
      :show-text="visibleChildren === 0 && nestLevel === 0"
    ></FilterAdd>
    <div class="filter-buttons">
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
import FilterTerm from './FilterTerm.vue';
import FilterAdd from './FilterAdd.vue';
import { mapGetters, mapMutations } from 'vuex';

export default {
  extends: FilterBase,
  name: 'FilterGroup',
  components: {
    FilterAdd,
    FilterTerm,
  },
  computed: {
    ...mapGetters(['getGroup']),
    ...mapGetters('results/query/filters', ['getChildren']),
    subTerms() {
      return this.getChildren(this.filterId, true)
        .filter((f) => {
          return !f.key.startsWith('group_');
        })
        .map((f) => f.key);
    },
    subGroups() {
      return this.getChildren(this.filterId, true)
        .filter((f) => {
          return f.key.startsWith('group_');
        })
        .map((f) => f.key);
    },
    visibleChildren() {
      return this.getChildren(this.filterId, true).filter((f) => {
        return !f.value.display.hidden;
      }).length;
    },
    readableGroupType() {
      return this.getGroup(this.filterKey);
    },
    showGroup() {
      return this.filterKey !== 'and' || this.nestLevel > 0;
    },
  },
  methods: {
    ...mapMutations('results/query/filters', ['changeKey']),
    changeGroupType() {
      let ix = this.schema.groups.indexOf(this.filterKey);
      let newIx = ix + 1 >= this.schema.groups.length ? 0 : ix + 1;
      let newGroup = this.schema.groups[newIx];
      this.changeKey({
        id: this.filterId,
        key: newGroup,
      });
    },
  },
};
</script>

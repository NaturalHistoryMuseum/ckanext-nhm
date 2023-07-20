<template>
  <div
    class="fields resourceid-list floating flex-container flex-column flex-left"
  >
    <div>
      <input
        type="checkbox"
        id="toggleAll"
        v-model="allResourcesToggle"
        @change="toggleAllResourceSelect"
      />
      <label for="toggleAll">Select all</label>
    </div>
    <span v-for="(pkg, index) in packageList" v-bind:key="pkg.id">
      <a
        href="javascript:void(0);"
        :id="pkg.id"
        :value="pkg.id"
        title="alt+click to select only this dataset"
        @click="packageClick(index, $event)"
        >{{ pkg.name }}</a
      >
      <div class="fields">
        <span v-for="resource in pkg.resources" v-bind:key="resource.id">
          <input
            type="checkbox"
            :id="resource.id"
            :value="resource.id"
            v-model="resourceIds"
          />
          <label :for="resource.id">{{ resource.name }}</label>
        </span>
      </div>
    </span>
  </div>
</template>

<script>
import { mapMutations, mapState, mapGetters } from 'vuex';

export default {
  name: 'ResourceList',
  data: function () {
    return {
      allResourcesToggle: false,
    };
  },
  computed: {
    ...mapState('results/query/resources', ['packageList']),
    ...mapGetters('results/query/resources', ['packageResources']),
    resourceIds: {
      get() {
        return this.$store.state.results.query.resources.resourceIds;
      },
      set(value) {
        this.setResourceIds(value);
      },
    },
  },
  methods: {
    ...mapMutations('results/query/resources', [
      'togglePackageResources',
      'selectAllResources',
      'setResourceIds',
    ]),
    toggleAllResourceSelect: function (event) {
      if (event.target.checked) {
        this.selectAllResources();
      } else {
        this.resourceIds = [];
      }
    },
    packageClick(index, event) {
      event.preventDefault();
      if (event.altKey) {
        this.resourceIds = this.packageResources(index);
      } else {
        this.togglePackageResources(index);
      }
    },
  },
  watch: {
    resourceIds: function (resourceIds, oldResourceIds) {
      if (resourceIds.length < oldResourceIds.length) {
        this.allResourcesToggle = false;
      }
    },
  },
};
</script>

<template>
  <div>
    <div class="biiif-thumbnail-header">
      <span class="biiif-status"> Found {{ total }} records</span>
      <a
        v-if="manifestLink"
        target="_blank"
        :href="manifestLink"
        class="biiif-manifest-link"
      >
        <img src="/images/iiif.png" alt="IIIF Manifest" />
      </a>
    </div>
    <ul class="nav nav-tabs">
      <li
        v-for="(args, tabName) in tabs"
        class="biiif-view-tab"
        :class="{ active: tabName === currentTab }"
      >
        <label>
          {{ tabName }}
          <input
            type="radio"
            :value="tabName"
            v-model="currentTab"
            class="sr-only"
          />
        </label>
      </li>
    </ul>
    <KeepAlive>
      <component :is="currentTab" v-bind="tabs[currentTab]" />
    </KeepAlive>
  </div>
</template>

<script>
import Gallery from './record-select-tabs/Gallery.vue';
import List from './record-select-tabs/List.vue';
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'RecordSelect',
  components: {
    Gallery,
    List,
  },
  data() {
    return {
      tabs: {
        Gallery: {
          bufferSize: 28,
          thumbnailSize: 120,
          fetchImmediately: false,
        },
        List: {
          bufferSize: 50,
          thumbnailSize: 60,
          fetchImmediately: true,
        },
      },
      currentTab: 'Gallery',
    };
  },
  computed: {
    ...mapState(['total', 'query']),
    ...mapGetters(['manifestLink']),
  },
  methods: {
    ...mapActions(['getRecordCount', 'getRecords']),
  },
  watch: {
    query: function () {
      this.getRecordCount();
      this.getRecords(this.tabs[this.currentTab].bufferSize || 50);
    },
  },
};
</script>

<style scoped></style>

<template>
  <div class="view-component">
    <LoadError v-if="loadError"></LoadError>
    <div class="flex-container flex-right">
      <small v-if="imageRecords"
        >{{ imageRecords.length }} images associated with {{ recordTag }}s
        {{ page * 100 + 1 }} - {{ page * 100 + records.length }}</small
      >
    </div>
    <div class="tiling-gallery full-width">
      <div
        v-for="(record, recordIndex) in loadedImageRecords"
        :key="`${record.record.data._id}-${record.image.id}`"
        class="gallery-tile"
      >
        <img
          @click="setViewerImage(recordIndex)"
          :src="record.image.thumb"
          :alt="record.image.title"
        />
        <small class="gallery-tile-title">
          <a
            :href="record.recordUrl"
            :aria-label="`Go to record ${record.record.data._id}`"
          >
            {{ record.recordTitle }}
          </a>
        </small>
        <small class="gallery-tile-number">
          {{ record.recordImageIndex + 1 }} / {{ record.imageTotal }}
        </small>
      </div>
    </div>
    <div
      class="flex-container flex-column flex-center pad-v space-children-v"
      v-if="brokenImageRecords.length > 0"
    >
      <Help
        :label="`${brokenImageRecords.length} thumbnail${
          brokenImageRecords.length > 1 ? 's' : ''
        } could not be loaded.`"
        popup-id="show-broken-imgs-help"
        ><small
          >If there are a lot of images not loading, check the banner at the top
          of the page to see if there's a known issue. Otherwise you can
          <a href="/contact">contact us</a>.</small
        ></Help
      >
      <small
        >View
        <i
          class="fas"
          :class="showBroken ? 'fa-caret-square-up' : 'fa-caret-square-down'"
          @click="showBroken = !showBroken"
        ></i
      ></small>
    </div>
    <div
      class="full-width flex-container flex-wrap flex-between tiling-gallery"
      v-if="showBroken"
    >
      <div
        v-for="(record, recordIndex) in brokenImageRecords"
        :key="`${record.record.data._id}-${record.image.id}`"
        class="gallery-tile gallery-tile-tiny gallery-tile-broken"
        alt="record.image.preview"
        role="img"
      >
        <small class="gallery-tile-title">
          <a :href="record.recordUrl">{{ record.recordTitle }}</a>
        </small>
        <small class="gallery-tile-number"
          >{{ record.recordImageIndex + 1 }} / {{ record.imageTotal }}</small
        >
      </div>
    </div>
  </div>
</template>

<script>
import BaseView from './BaseView.vue';
import Loading from '../Loading.vue';
import LoadError from '../LoadError.vue';

import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
import Help from '../popups/Help.vue';

export default {
  extends: BaseView,
  name: 'GalleryView',
  data: function () {
    return {
      loading: true,
      loadError: false,
      presetData: {
        key: 'hasImage',
        parent: 'group_root',
        display: {
          hidden: true,
          temp: true,
        },
      },
      showBroken: false,
    };
  },
  components: {
    Help,
    Loading,
    LoadError,
  },
  computed: {
    ...mapState('results/display', ['recordTag']),
    ...mapGetters('results/query/filters', ['hasFilter']),
    brokenImageRecords() {
      return this.imageRecords.filter(
        (r) => !r.image.loading && !r.image.canLoad,
      );
    },
  },
  methods: {
    ...mapMutations('results/display', ['setFilteredRecordTag']),
    ...mapActions('results', ['runSearch']),
    ...mapActions('results/query/filters', ['addPreset']),
    loadFailed() {
      this.loading = false;
      this.loadError = true;
    },
  },
  created() {
    this.loading = true;
    this.addPreset(this.presetData)
      .then((wasAdded) => {
        if (wasAdded) {
          return this.runSearch(0);
        } else {
          return new Promise((resolve) => {
            resolve();
          });
        }
      })
      .then(this.loadAndCheckImages)
      .then(() => {
        this.setFilteredRecordTag(this.recordTag + '$ with images');
        this.loading = false;
      });
  },
};
</script>

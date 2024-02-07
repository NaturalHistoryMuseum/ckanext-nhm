<template>
  <div class="view-component">
    <LoadError v-if="loadError"></LoadError>
    <div class="flex-container flex-right">
      <small v-if="imageRecords"
        >{{ imageRecords.length }} images associated with {{ recordTag }}s
        {{ page * 100 + 1 }} - {{ page * 100 + records.length }}</small
      >
    </div>
    <div class="tiling-gallery full-width" ref="galleryContainer">
      <div
        v-for="(record, recordIndex) in loadedImageRecords"
        :key="`${record.record.data._id}-${record.image.id}`"
        class="gallery-tile"
        :style="{ gridRowEnd: `span ${imageHeight(record)}` }"
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
      class="full-width flex-container flex-wrap flex-between tiling-gallery tiny-tiling-gallery"
      v-if="showBroken"
    >
      <div
        v-for="(record, recordIndex) in brokenImageRecords"
        :key="`${record.record.data._id}-${record.image.id}`"
        class="gallery-tile gallery-tile-tiny gallery-tile-broken"
        :alt="record.image.preview"
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

import debounce from 'lodash.debounce';

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
      // we could get these automatically but they won't change much so it's just unnecessary processing
      minColWidth: 260, // grid-col-gap + grid-template-cols; set in css
      defaultRowHeight: 10, // grid-row-gap + grid-auto-rows; set in css
      // this will be set automatically
      colWidth: 0,
    };
  },
  components: {
    Help,
    Loading,
    LoadError,
  },
  computed: {
    ...mapState('results/display', ['recordTag']),
    ...mapState('results/query/resources', ['resourceIds']),
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
    imageHeight(imageRecord) {
      const height = this.colWidth / imageRecord.image.ratio;
      const rowHeight =
        (height + this.defaultRowHeight) / this.defaultRowHeight;

      // using Math.ceil completely breaks webpack so we have to do it this weird way
      return rowHeight - (rowHeight % 1) + 1;
    },
    setColWidth() {
      let currentWidth = 0;
      try {
        currentWidth = this.$refs.galleryContainer.clientWidth;
      } catch {
        //
      }

      if (currentWidth === 0) {
        // the container is about 88% of the full window width; this is here just in
        // case the container hasn't loaded yet
        currentWidth = window.innerWidth * 0.88;
      }
      // essentially Math.floor
      const cols =
        currentWidth / this.minColWidth -
        ((currentWidth / this.minColWidth) % 1);
      // Math.ceil
      this.colWidth = currentWidth / cols - ((currentWidth / cols) % 1) + 1;
    },
  },
  created() {
    this.loading = true;
    this.addPreset(this.presetData)
      .then((wasAdded) => {
        return this.runSearch(0);
      })
      .then(() => {
        this.setFilteredRecordTag(this.recordTag + '$ with images');
        this.loading = false;
      });
  },
  mounted() {
    // give the container a chance to load
    setTimeout(this.setColWidth, 500);
    const debouncedSetColWidth = debounce(this.setColWidth, 100);
    window.addEventListener('resize', () => {
      debouncedSetColWidth();
    });
  },
  watch: {
    resourceIds() {
      this.addPreset(this.presetData);
    },
  },
};
</script>

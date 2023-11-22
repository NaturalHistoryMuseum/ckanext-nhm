<template>
  <div
    class="record-select-view biiif-thumbnail-track-container"
    ref="track"
    @scroll="onScroll"
    :style="{ height: `${rowHeight * 2.3}px` }"
  >
    <div
      class="biiif-thumbnail-track"
      :style="{
        gridTemplateColumns: `repeat(auto-fill, minmax(${colWidth}px, 1fr))`,
        gridAutoRows: `${rowHeight}px`,
      }"
    >
      <div
        :class="{
          'biiif-thumbnail-container': true,
          active: currentIndex === index,
        }"
        :style="{ height: `${rowHeight}px` }"
        v-for="(record, index) in records"
        role="button"
        :aria-pressed="currentIndex === index ? 'true' : 'false'"
        :key="record.data._id"
        :data-thumbnail-index="index"
        ref="container"
        @click="goto(index)"
      >
        <img
          class="biiif-thumbnail-image"
          :style="{ height: `${thumbnailSize}px` }"
          :src="getRecordThumbnail(record)"
          :height="`${thumbnailSize}px`"
          draggable="false"
          :alt="`Thumbnail of ${record.data['Barcode']} from ${record.data['Collection Name']}`"
        />
        <div class="biiif-thumbnail-label">
          <div class="biiif-thumbnail-label-barcode">
            {{ record.data['Barcode'] }}
          </div>
          <div class="biiif-thumbnail-label-collection">
            {{ record.data['Collection Name'] }}
          </div>
        </div>
      </div>
      <div
        class="biiif-thumbnail-container"
        :style="{ height: `${rowHeight}px`, cursor: 'default' }"
      >
        <div
          class="flex-container flex-center flex-around"
          :style="{ height: `${thumbnailSize}px` }"
          v-if="loading.results"
        >
          <i class="fas fa-spinner fa-spin fa-2x"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Base from './Base.vue';

export default {
  name: 'Gallery',
  extends: Base,
  computed: {
    rowHeight() {
      // css vars
      const vPadding = 20;
      const gridGap = 5;
      const labelHeight = 60; // this is an estimate

      return this.thumbnailSize + vPadding + gridGap + labelHeight;
    },
    colWidth() {
      // css vars
      const hPadding = 20;

      const imgWidthEstimate = this.thumbnailSize * (4 / 3); // most images are about 4:3
      return imgWidthEstimate + hPadding;
    },
  },
};
</script>

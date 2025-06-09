<template>
  <div class="image-viewer" @click.self="hideImage">
    <div class="flex-container flex-stretch-first image-viewer-header">
      <h4>
        <a :href="viewerImage.recordUrl" title="View record">
          {{ viewerImage.image.title }}
          <i class="fas fa-arrow-right fa-xs inline-icon-right"></i>
        </a>
      </h4>
      <div class="info-popup-button">
        <a
          class="image-viewer-icon"
          title="View in large image viewer"
          :href="livUrl"
          target="_blank"
        >
          <i class="fas fa-search-plus fa-2x"></i>
        </a>
      </div>
      <div class="info-popup-button">
        <a
          class="image-viewer-icon"
          title="Download original image"
          :href="viewerImage.image.download"
        >
          <i class="fas fa-cloud-download-alt fa-2x"></i>
        </a>
      </div>
      <a
        class="image-viewer-icon"
        title="Close image viewer"
        @click="hideImage"
      >
        <i class="fas fa-times fa-2x"></i>
      </a>
    </div>
    <div class="scrolling-arrows">
      <div class="scroll-left" @click="previousImage" v-if="!firstImage">
        <i class="fas fa-angle-double-left"></i>
      </div>
      <div class="scroll-right" @click="nextImage" v-if="!lastImage">
        <i class="fas fa-angle-double-right"></i>
      </div>
    </div>
    <img
      v-images-loaded:on.done="loadImage"
      :src="viewerImage.image.preview"
      :alt="viewerImage.image.title"
      class="main-image"
      :class="{ loading: loading }"
    />
    <Loading v-if="loading"></Loading>
    <div class="flex-container flex-center image-viewer-footer">
      <small>Licence:</small>
      <a :href="viewerImage.image.licence.url">
        <small>{{ viewerImage.image.licence.title }}</small>
      </a>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapMutations, mapState } from 'vuex';
import imagesLoaded from 'vue-images-loaded';
import Loading from '../Loading.vue';
import LoadError from '../LoadError.vue';

export default {
  name: 'ImageViewer',
  data: function () {
    return {
      loading: true,
      loadError: false,
      email: null,
      showDownload: false,
      download: null,
    };
  },
  directives: {
    imagesLoaded,
  },
  components: {
    Loading,
    LoadError,
  },
  computed: {
    ...mapState('results/display', ['viewerImageIndex', 'viewerImagePage']),
    ...mapGetters('results/display', ['viewerImage']),
    firstImage() {
      return this.viewerImageIndex === 0;
    },
    lastImage() {
      return this.viewerImagePage.length <= this.viewerImageIndex + 1;
    },
    livUrl() {
      const resource = this.viewerImage.record.resource;
      const recordId = this.viewerImage.record.data._id;
      const imageIx = this.viewerImage.recordImageIndex;
      return `/image-viewer/record/${resource}/${recordId}/${imageIx}`;
    },
  },
  methods: {
    ...mapMutations('results/display', ['hideImage', 'setViewerImage']),
    previousImage() {
      if (!this.firstImage) {
        this.changeImage(this.viewerImageIndex - 1);
      }
    },
    nextImage() {
      if (!this.lastImage) {
        this.changeImage(this.viewerImageIndex + 1);
      }
    },
    changeImage(index) {
      this.loading =
        this.viewerImage.image.preview !==
        this.viewerImagePage[index].image.preview;
      this.setViewerImage(index);
    },
    keyListener(event) {
      if (event.key === 'ArrowRight') {
        this.nextImage();
      } else if (event.key === 'ArrowLeft') {
        this.previousImage();
      } else if (event.key === 'Escape') {
        this.hideImage();
      }
    },
    loadImage(instance) {
      this.loading = false;
      this.loadError = instance.hasAnyBroken;
    },
  },
  mounted() {
    $(document).on('keyup', this.keyListener);
  },
  beforeDestroy() {
    $(document).off('keyup', this.keyListener);
  },
};
</script>

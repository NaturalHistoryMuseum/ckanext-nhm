<template>
  <div>
    <div class="biiif-thumbnail-header">
      <span class="biiif-status"> Found {{ total }} records </span>
      <a
        v-if="manifestLink"
        target="_blank"
        :href="manifestLink"
        class="biiif-manifest-link"
      >
        <img src="/images/iiif.png" alt="IIIF Manifest" />
      </a>
    </div>
    <div
      class="biiif-thumbnail-track"
      @mousedown="onMouseDown"
      @mouseleave="onMouseLeave"
      @mouseup="onMouseUp"
      @mousemove="onMouseMove"
      @scroll="onScroll"
      @contextmenu="onRightClick"
      ref="track"
    >
      <div
        :class="{
          'biiif-thumbnail-container': true,
          active: currentIndex === index,
        }"
        v-for="(record, index) in records"
        role="button"
        :aria-pressed="currentIndex === index ? 'true' : 'false'"
        :key="record.data._id"
        :data-thumbnail-index="index"
        ref="container"
      >
        <img
          class="biiif-thumbnail-image"
          :src="getRecordThumbnail(record)"
          :width="`${thumbnailSize}px`"
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
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { api, SET_RECORD } from '../app';

export default {
  name: 'ThumbnailCarousel',
  props: {
    bufferSize: {
      type: Number,
      default: 15,
    },
    thumbnailSize: {
      type: Number,
      default: 200,
    },
    mouseClickMoveThreshold: {
      type: Number,
      default: 5,
    },
    fetchImmediately: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      records: [],
      total: 0,
      source: null,
      currentIndex: 0,
      sliding: false,
      isDown: false,
      startX: 0,
      scrollLeft: 0,
      waitingForMore: false,
    };
  },
  computed: {
    ...mapState(['query']),
    /**
     * Returns the manifest URL for the current record, or false.
     *
     * @returns {boolean|str} if there's no current record, returns false, otherwise the returns
     *                        the manifest URL
     */
    manifestLink() {
      if (!!this.records[this.currentIndex]) {
        return this.records[this.currentIndex].iiif.id;
      }
      return false;
    },
    /**
     * Determines whether there are more records available or not.
     *
     * @returns {boolean} true if there are more records to fetch, false if not
     */
    moreRecordsAvailable() {
      return this.records.length < this.total;
    },
  },
  async created() {
    if (this.fetchImmediately) {
      await this.getRecords();
    }
  },
  methods: {
    /**
     * Retrieves records from the multisearch API.
     *
     * @param isMoreRequest whether this is a request for more data or not
     */
    async getRecords(isMoreRequest = false) {
      if (this.query === null) {
        // if there is now query, shortcut a no records update
        this.records = [];
        this.total = 0;
        this.source = null;
      } else {
        if (!isMoreRequest) {
          // if it's not a request for more records, reset the async iterable source
          this.source = api.getRecords();
          // and update the total
          this.total = await api.getRecordCount();
        }
        // read bufferSize records from the API
        let newRecords = [];
        for (let i = 0; i < this.bufferSize; i++) {
          const next = await this.source.next();
          if (next.done) {
            break;
          }
          newRecords.push(next.value);
        }
        // then update the records
        if (isMoreRequest) {
          this.records.push(...newRecords);
        } else {
          this.records = [...newRecords];
          // we've reset the records, move the track back to the start
          this.goto(0);
        }
      }
    },
    /**
     * Returns the thumbnail URL for the given record.
     *
     * @param record the record Object
     * @returns {string} the URL or the empty string if the URL cannot be formed
     */
    getRecordThumbnail(record) {
      if (!!record.iiif) {
        // TODO: what about non-iiif images?
        const baseUrl = record.iiif.items[0].items[0].items[0].body.id;
        return `${baseUrl}/full/${this.thumbnailSize},/0/default.jpg`;
      }
      return '';
    },
    onMouseDown(event) {
      this.isDown = true;
      this.sliding = true;
      this.startX = event.pageX;
      this.scrollLeft = this.$refs.track.scrollLeft;
    },
    onRightClick() {
      // just use the mouse leave logic
      this.onMouseLeave();
    },
    onMouseLeave() {
      this.isDown = false;
      this.sliding = false;
    },
    onMouseUp(event) {
      this.isDown = false;
      this.sliding = false;
      if (
        this.startX >= event.pageX - this.mouseClickMoveThreshold &&
        this.startX <= event.pageX + this.mouseClickMoveThreshold
      ) {
        let index = null;
        if (
          event.target.classList.contains('biiif-thumbnail-image') ||
          event.target.classList.contains('biiif-thumbnail-label')
        ) {
          index = parseInt(event.target.parentElement.dataset.thumbnailIndex);
        } else if (
          event.target.classList.contains('biiif-thumbnail-container')
        ) {
          index = parseInt(event.target.dataset.thumbnailIndex);
        }
        if (index != null) {
          this.goto(index);
        }
      }
    },
    onMouseMove(event) {
      if (!this.isDown) return;
      event.preventDefault();
      const x = event.pageX;
      const walk = x - this.startX;
      this.$refs.track.scrollLeft = this.scrollLeft - walk;
    },
    onScroll(event) {
      if (!this.waitingForMore && this.moreRecordsAvailable) {
        const scroll = event.target.scrollLeft + event.target.offsetWidth;
        if (scroll / event.target.scrollWidth >= 0.9) {
          this.waitingForMore = true;
          this.getRecords(true);
        }
      }
    },
    /**
     * Update the currently selected record to the record at the given index. Note that this
     * doesn't move the track, it just updates the internal state.
     *
     * @param index the record index to select
     */
    goto(index) {
      this.currentIndex = index;
      let newRecord = null;
      if (this.records.length > 0) {
        newRecord = this.records[index];
      }
      this.$store.commit(SET_RECORD, newRecord);
    },
  },
  watch: {
    records(newRecords, oldRecords) {
      this.waitingForMore = false;

      if (
        oldRecords.length > 0 &&
        newRecords.length > 0 &&
        oldRecords[0]._id !== newRecords[0]._id
      ) {
        this.$refs.track.scrollLeft = 0;
        this.goto(0);
      }
    },
    '$store.state.query': function () {
      this.getRecords();
    },
  },
};
</script>

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
      class="biiif-thumbnail-track-container"
      ref="track"
      @scroll="onScroll"
      :style="{ height: `${rowHeight * 2.3}px` }"
    >
      <div
        class="biiif-thumbnail-track"
        :style="{
          gridTemplateColumns: `repeat(auto-fill, minmax(${colWidth}px, 1fr))`,
          gridAutoRows: `${rowHeight}px`,
          minHeight: `${rowHeight * 3}px`,
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
      default: 150,
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
      scrollDown: 0,
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
        return `${baseUrl}/full/,${this.thumbnailSize}/0/default.jpg`;
      }
      return '';
    },
    onScroll(event) {
      if (!this.waitingForMore && this.moreRecordsAvailable) {
        const scroll = event.target.scrollTop + event.target.offsetHeight;
        if (scroll / event.target.scrollHeight >= 0.9) {
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
        this.$refs.track.scrollDown = 0;
        this.goto(0);
      }
    },
    '$store.state.query': function () {
      this.getRecords();
    },
  },
};
</script>

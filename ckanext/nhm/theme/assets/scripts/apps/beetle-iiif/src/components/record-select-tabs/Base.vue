<template></template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'Base',
  props: {
    bufferSize: {
      type: Number,
      default: 15,
    },
    fetchImmediately: {
      type: Boolean,
      default: true,
    },
    thumbnailSize: {
      type: Number,
      default: 100,
    },
  },
  data() {
    return {
      currentIndex: 0,
      scrollDown: 0,
      waitingForMore: false,
    };
  },
  computed: {
    ...mapState(['query', 'total', 'records', 'loading']),
    /**
     * Determines whether there are more records available or not.
     *
     * @returns {boolean} true if there are more records to fetch, false if not
     */
    moreRecordsAvailable() {
      return this.records.length < this.total;
    },
  },
  methods: {
    ...mapActions(['getRecords', 'getRecordCount']),
    onScroll(event) {
      if (!this.waitingForMore && this.moreRecordsAvailable) {
        const scroll = event.target.scrollTop + event.target.offsetHeight;
        if (scroll / event.target.scrollHeight >= 0.9) {
          this.waitingForMore = true;
          this.getRecords(this.bufferSize);
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
      this.$store.commit('SET_RECORD', newRecord);
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
  },
  watch: {
    records(newRecords, oldRecords) {
      this.waitingForMore = false;

      if (newRecords.length > 0 && oldRecords[0]._id !== newRecords[0]._id) {
        this.$refs.track.scrollTop = 0;
        this.goto(0);
      }
    },
  },
};
</script>

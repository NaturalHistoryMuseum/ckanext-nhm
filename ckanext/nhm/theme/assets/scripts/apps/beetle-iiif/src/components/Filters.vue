<template>
  <div class="module module-narrow module-shallow">
    <h2 class="module-heading">
      <i class="fas fa-filter fa-lg inline-icon-left"></i>Filters
    </h2>
    <div class="module-content">
      <div>
        If you know what drawer you're looking for, please select its barcode
        from the dropdown below. If not, use the checkboxes to filter your
        search by collection.
      </div>
      <div class="biiif-intro-text-lower">
        Please be aware that you cannot use both of these options at the same
        time.
      </div>
      <hr />
      <div
        :class="{ 'biiif-filter': true, active: activeFilter === 'barcode' }"
      >
        <label
          class="biiif-filter-barcode-label"
          for="biiif-filter-barcode-select"
        >
          Select a barcode:
        </label>
        <div class="biiif-filter-barcode-body">
          <select id="biiif-filter-barcode-select" v-model="barcode">
            <option disabled value="">Please select one</option>
            <option v-for="option in barcodes" :value="option" :key="option">
              {{ option }}
            </option>
          </select>
          <button
            class="btn btn-primary biiif-button"
            :disabled="barcode == null"
            @click="changeBarcode"
          >
            View drawer
          </button>
        </div>
      </div>
      <hr />
      <div
        :class="{
          'biiif-filter': true,
          active: activeFilter === 'collections',
        }"
      >
        <div class="biiif-filter-collection-label-header">
          Or choose one or more collections to view:
        </div>
        <div v-for="option in collectionNames">
          <label class="biiif-filter-collection-label">
            <input type="checkbox" :value="option" v-model="collections" />
            {{ option }}
          </label>
        </div>
        <div class="biiif-filter-collection-actions">
          <div class="biiif-filter-collection-selectors">
            <span class="biiif-filter-collection-selector" @click="selectAll"
              >Select all</span
            >
            <span class="biiif-filter-collection-selector" @click="deselectAll"
              >Clear</span
            >
          </div>
          <button
            class="btn btn-primary biiif-button"
            :disabled="collections.length === 0"
            @click="changeCollections"
          >
            {{ 'View collection' | pluralize(collections) }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api, SET_QUERY } from '../app';

export default {
  name: 'Filters',
  data() {
    return {
      // a list of all the available barcodes
      barcodes: [],
      // a list of all the available collection names
      collectionNames: [],
      // the currently selected barcode (or null if no barcode is selected)
      barcode: null,
      // the list of currently selected collections (empty list if none are selected)
      collections: [],
      // the name of the currently active filter (either 'collections' or 'barcode')
      activeFilter: null,
    };
  },
  async created() {
    // first, run through all the records and grab all the barcodes and all the available
    // collection names. We could use the autocomplete API to get these values but because we
    // want to get all the barcodes, and they are unique, we'll end up going through all records
    // anyway and this way is more efficient than calling the autocomplete endpoint.
    let barcodes = [];
    let names = [];
    for await (const record of api.getRecords(500, false)) {
      const barcode = record.data['Barcode'];
      // this is technically not needed but hey why not
      if (!barcodes.includes(barcode)) {
        barcodes.push(barcode);
      }
      const name = record.data['Collection Name'];
      if (!names.includes(name)) {
        names.push(name);
      }
    }

    // add all the barcodes and collection names in alphabetical order
    this.barcodes.push(...barcodes.sort());
    this.collectionNames.push(...names.sort());

    // start off with everything selected
    this.selectAll();
    this.changeCollections();
  },
  methods: {
    /**
     * Select all the available collections.
     */
    selectAll() {
      for (const collection of this.collectionNames) {
        if (!this.collections.includes(collection)) {
          this.collections.push(collection);
        }
      }
    },
    /**
     * Clear the collection names selection.
     */
    deselectAll() {
      this.collections = [];
    },
    /**
     * Changes the current store state's query to a new query using the currently selected
     * collections to filter the results.
     */
    changeCollections() {
      this.activeFilter = 'collections';
      let query;
      switch (this.collections.length) {
        case 0:
          query = null;
          break;
        case 1:
          query = {
            string_equals: {
              fields: ['Collection Name'],
              value: this.collections[0],
            },
          };
          break;
        default:
          query = {
            or: this.collections.map((collection) => ({
              string_equals: {
                fields: ['Collection Name'],
                value: collection,
              },
            })),
          };
          break;
      }
      // update the query in the store state
      this.$store.commit(SET_QUERY, query);
    },
    /**
     * Changes the current store state's query to a new query using the currently selected
     * barcode to filter the results.
     */
    changeBarcode() {
      this.activeFilter = 'barcode';
      this.$store.commit(SET_QUERY, {
        string_equals: {
          fields: ['Barcode'],
          value: this.barcode,
        },
      });
    },
  },
  filters: {
    pluralize: function (value, collections) {
      if (collections.length > 1) {
        return `${value}s`;
      }
      return value;
    },
  },
};
</script>

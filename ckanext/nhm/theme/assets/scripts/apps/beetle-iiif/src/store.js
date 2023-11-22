import Vue from 'vue';
import Vuex from 'vuex';
import api from './api';

Vue.use(Vuex);

const rootElement = document.getElementById('beetle-iiif-app');
const resourceId = rootElement.getAttribute('data-resource-id');

// this is the base query used for all API search calls, it excludes any record that doesn't have
// an image field
const baseQuery = {
  filters: {
    and: [
      {
        // the Image field must exist
        exists: {
          fields: ['Image'],
        },
      },
      {
        // the Image field must not have the empty string as the value
        not: [
          {
            string_equals: {
              fields: ['Image'],
              value: '',
            },
          },
        ],
      },
    ],
  },
};

const store = new Vuex.Store({
  state: {
    resourceId: resourceId,
    query: {},
    record: null,
    source: null,
    records: [],
    total: 0,
    _filterValues: {
      barcodes: [],
      collections: [],
    },
    loading: {
      filters: false,
      results: false,
    },
  },
  getters: {
    /**
     * Utility function used to build a search body Object. The baseQuery will always be included
     * but the current store state's query is optionally included. The resulting Object can be
     * POSTed directly to the multisearch endpoint and used as a base for many of the related
     * endpoints too.
     *
     * @param size the size of the response to request (i.e. number of hits), defaults to 15
     * @param useQuery whether to use the store state's query or not, defaults to true
     * @returns {{size: number, query: Object, resource_ids: (string)[]}} the body Object
     */
    getSearchBody:
      (state) =>
      (size = 15, useQuery = true) => {
        // make a copy of the baseQuery
        const query = JSON.parse(JSON.stringify(baseQuery));
        // only add the store state's query if it's asked for and defined
        if (useQuery && Object.keys(state.query).length > 0) {
          // add the current query
          query.filters.and.push(state.query);
        }
        return {
          resource_ids: [state.resourceId],
          query: query,
          size: size,
        };
      },
    barcodes: (state) => {
      return [...state._filterValues.barcodes].sort();
    },
    collectionNames: (state) => {
      return [...state._filterValues.collections].sort();
    },
    manifestLink: (state) => {
      if (!!state.record) {
        return state.record.iiif.id;
      }
      return false;
    },
    columnNames: (state) => {
      if (!state.records) {
        return [];
      }
      return Object.keys(state.records[0].data).filter(
        (k) => !k.startsWith('_') && k !== 'Image',
      );
    },
  },
  mutations: {
    SET_RECORD(state, newRecord) {
      Vue.set(state, 'record', newRecord);
    },
    SET_QUERY(state, newQuery) {
      Vue.set(state, 'query', newQuery);
      Vue.set(state, 'source', null);
      Vue.set(state, 'records', []);
      Vue.set(state, 'record', null);
      Vue.set(state, 'total', 0);
    },
  },
  actions: {
    async getFilterValues(context) {
      const queryBody = context.getters.getSearchBody(500, false);
      Vue.set(context.state.loading, 'filters', true);

      for await (const barcode of api.autocomplete(
        { ...queryBody },
        'Barcode',
      )) {
        if (!context.state._filterValues.barcodes.includes(barcode)) {
          context.state._filterValues.barcodes.push(barcode.toUpperCase());
        }
      }

      for await (const colName of api.autocomplete(
        { ...queryBody },
        'Collection Name',
      )) {
        context.state._filterValues.collections.push(
          colName.replace('bmnh', 'BMNH'),
        );
      }

      Vue.set(context.state.loading, 'filters', false);
    },

    async getRecordCount(context) {
      const queryBody = context.getters.getSearchBody(0);
      const total = await api.getRecordCount(queryBody);
      Vue.set(context.state, 'total', total);
    },

    async getRecords(context, bufferSize = 0) {
      Vue.set(context.state.loading, 'results', true);

      // this opens a request for 100 records, if one isn't open already
      const queryBody = context.getters.getSearchBody(100);
      if (context.state.source == null) {
        Vue.set(context.state, 'source', api.getRecords(queryBody));
      }

      // this loads these into state.records in bufferSize chunks if bufferSize is set,
      // or all at once if not
      let i = 0;
      while (bufferSize ? i < bufferSize : true) {
        const next = await context.state.source.next();
        if (next.done) {
          break;
        }
        context.state.records.push(next.value);
        i++;
      }

      if (!context.state.record) {
        context.commit('SET_RECORD', context.state.records[0]);
      }

      Vue.set(context.state.loading, 'results', false);
    },
  },
});

export default store;

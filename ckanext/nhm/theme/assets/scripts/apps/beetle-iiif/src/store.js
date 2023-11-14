import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const rootElement = document.getElementById('beetle-iiif-app');
const resourceId = rootElement.getAttribute('data-resource-id');

const store = new Vuex.Store({
  state: {
    resourceId: resourceId,
    query: {},
    record: null,
  },
  mutations: {
    SET_RECORD(state, newRecord) {
      state.record = newRecord;
    },
    SET_QUERY(state, newQuery) {
      state.query = newQuery;
    },
  },
});

export default store;

import resources from './resources';
import filters from './filters';
import Vue from 'vue';

let query = {
  namespaced: true,
  modules: {
    resources,
    filters,
  },
  state: {
    search: null,
    after: null,
    version: null,
  },
  getters: {
    requestBody: (state, getters) => (ignoreTemp) => {
      ignoreTemp = ignoreTemp || false;
      let body = {
        query: getters.queryBody(ignoreTemp),
        resource_ids: getters['resources/sortedResources'],
      };

      if (state.after != null) {
        body.after = state.after;
      }

      if (state.version != null) {
        body.version = state.version;
      }

      return body;
    },
    queryBody: (state, getters) => (ignoreTemp) => {
      ignoreTemp = ignoreTemp || false;
      let body = {};
      if (state.search !== null && state.search !== '') {
        body.search = state.search;
      }

      if (getters['filters/count'](ignoreTemp) > 1) {
        let filters = getters['filters/queryfy']('group_root', ignoreTemp);
        if (Object.keys(filters).length > 0) {
          body.filters = filters;
        }
      }
      return body;
    },
  },
  mutations: {
    setSearch(state, searchString) {
      state.search = searchString;
    },
    setAfter(state, after) {
      state.after = after;
    },
  },
  actions: {
    setRequestBody(context, newBody) {
      Vue.set(context.rootState.appState.query, 'querySource', null);
      Vue.set(context.rootState.appState.query, 'warnings', []);

      let resourceIdsPromise = new Promise((resolve, reject) => {
        Vue.set(
          context.rootState.appState.query.parsingError,
          'resourceIds',
          context.getters['resources/invalidResourceIds'](newBody.resource_ids),
        );

        if (
          context.rootState.appState.query.parsingError.resourceIds === null
        ) {
          context.commit('resources/setResourceIds', newBody.resource_ids);
          resolve();
        } else {
          reject();
        }
      });

      let filtersPromise = context
        .dispatch('filters/setFromQuery', newBody.query || {})
        .then(() => {
          Vue.set(
            context.rootState.appState.query.parsingError,
            'queryBody',
            context.state.filters.parsingError,
          );
          if (
            context.rootState.appState.query.parsingError.queryBody !== null
          ) {
            throw Error;
          }

          if (
            newBody.query !== undefined &&
            newBody.query.search !== undefined
          ) {
            context.state.search = newBody.query.search.toString();
          }
        });

      if (newBody.after != null) {
        context.state.after = newBody.after;
      }

      if (newBody.version != null) {
        context.state.version = newBody.version;
      }

      return Promise.all([resourceIdsPromise, filtersPromise]);
    },
  },
};

export default query;

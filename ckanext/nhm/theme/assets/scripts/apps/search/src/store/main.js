import Vue from 'vue';
import Vuex from 'vuex';
import results from './results/main';
import appState from './appState';
import $RefParser from 'json-schema-ref-parser';
import * as d3 from 'd3-collection';
import { get, post } from './utils';
import pako from 'pako';
import router from '../router';

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    results,
    appState,
  },
  state: {
    schema: {
      groups: [],
      terms: {},
      raw: {},
    },
  },
  getters: {
    getGroup: (state) => (groupId) => {
      return {
        and: 'ALL OF',
        or: 'ANY OF',
        not: 'NONE OF',
      }[groupId];
    },
  },
  mutations: {},
  actions: {
    getSchema(context) {
      context.state.appState.app.loading = true;
      context.state.appState.app.error = false;
      let schemaPath = '/querySchemas/v1.0.0/v1.0.0.json';
      return $RefParser
        .dereference(schemaPath, { resolve: { http: { timeout: 2000 } } })
        .then((data) => {
          let groups = d3.keys(data.definitions.group.properties);
          let terms = d3
            .nest()
            .key((t) => (t.key.includes('_') ? t.key.split('_')[0] : 'other'))
            .rollup((leaves) =>
              leaves.map((l) => l.key.slice(l.key.indexOf('_') + 1) || ''),
            )
            .object(d3.entries(data.definitions.term.properties));
          return {
            groups: groups,
            terms: terms,
            raw: data,
          };
        })
        .then(
          (schema) => {
            context.state.schema = schema;
            context.state.appState.app.loading = false;
          },
          (error) => {
            context.state.appState.app.loading = false;
            context.state.appState.app.error = true;
          },
        );
    },
    resolveUrl(context, route) {
      let slug = route.params.slug;
      let pageParam = route.query.page;
      let viewParam = route.query.view;
      if (slug === undefined || slug === '') {
        context.commit('results/query/filters/resetFilters');
        return;
      }
      post('datastore_resolve_slug', {
        slug: slug,
      })
        .then((data) => {
          if (data.success) {
            context
              .dispatch('results/query/setRequestBody', data.result)
              .then(() => {
                let page = 0;
                if (pageParam !== undefined) {
                  try {
                    let compressedString = Buffer.from(pageParam, 'base64');
                    let afterList = JSON.parse(
                      pako.inflate(compressedString, { to: 'string' }),
                    );
                    if (afterList.length > 1) {
                      afterList.forEach((a) => {
                        context.commit('results/addPage', a);
                      });
                      page = afterList.length - 1;
                    }
                  } catch (error) {
                    console.log(error);
                  }
                }
                if (viewParam !== undefined) {
                  context.commit('results/display/setView', viewParam);
                }
                context.dispatch('results/runSearch', page);
              });
          } else {
            throw Error;
          }
        })
        .catch((error) => {
          context.commit('results/query/filters/resetFilters');
        })
        .finally(() => {
          router.replace({ query: {}, params: {}, path: '/search' });
        });
    },
    getUser(context) {
      return post('user_show')
        .then((d) => {
          return {
            loggedIn: true,
            sysAdmin: d.result.sysadmin,
          };
        })
        .catch((e) => {
          return {
            loggedIn: false,
            sysAdmin: false,
          };
        });
    },
  },
});

export default store;

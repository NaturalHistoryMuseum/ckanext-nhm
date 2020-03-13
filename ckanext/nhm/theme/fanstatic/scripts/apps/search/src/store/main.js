import Vue from 'vue';
import Vuex from 'vuex';
import results from './results/main';
import $RefParser from 'json-schema-ref-parser';
import * as d3 from 'd3-collection';
import {post} from './utils';
import pako from 'pako';
import router from '../router';

Vue.use(Vuex);

const store = new Vuex.Store(
    {
        modules:   {
            results
        },
        state:     {
            appLoading: false,
            appError:   false,
            schema:     {
                groups: [],
                terms:  {},
                raw:    {}
            }
        },
        getters:   {
            getGroup: state => groupId => {
                return {
                    'and': 'ALL OF',
                    'or':  'ANY OF',
                    'not': 'NONE OF'
                }[groupId];
            },
        },
        mutations: {},
        actions:   {
            getSchema(context) {
                context.state.appLoading = true;
                context.state.appError   = false;
                let schemaPath           = '/querySchemas/v1.0.0/v1.0.0.json';
                $RefParser.dereference(schemaPath, {resolve: {http: {timeout: 2000}}})
                          .then(data => {
                              let groups = d3.keys(data.definitions.group.properties);
                              let terms  = d3.nest()
                                             .key(t => t.key.includes('_') ? t.key.split('_')[0] : 'other')
                                             .rollup(leaves => leaves.map((l) => l.key.slice(l.key.indexOf('_') + 1) || ''))
                                             .object(d3.entries(data.definitions.term.properties));
                              return {
                                  groups: groups,
                                  terms:  terms,
                                  raw:    data
                              };
                          })
                          .then(schema => {
                              context.state.schema     = schema;
                              context.state.appLoading = false;
                          }, error => {
                              context.state.appLoading = false;
                              context.state.appError   = true;
                          });
            },
            resolveUrl(context, route) {
                let slug      = route.params.slug;
                let pageParam = route.query.page;
                let viewParam = route.query.view;
                if (slug === undefined || slug === '') {
                    context.commit('results/query/filters/resetFilters');
                    return;
                }
                post('datastore_resolve_slug', {
                    slug: slug
                }).then(data => {
                    if (data.success) {
                        context.dispatch('results/query/setRequestBody', data.result);

                        let page = 0;
                        if (pageParam !== undefined) {
                            try {
                                let compressedString = Buffer.from(pageParam, 'base64');
                                let afterList        = JSON.parse(pako.inflate(compressedString, {to: 'string'}));
                                if (afterList.length > 1) {
                                    afterList.forEach(a => {
                                        context.commit('results/addPage', a)
                                    })
                                    page = afterList.length - 1;
                                }
                            } catch (error) {
                                console.log(error);
                            }
                        }
                        if (viewParam !== undefined) {
                            context.commit('results/display/setView', viewParam);
                        }
                        router.replace({query: {}, params: {}, path: '/search'})
                        context.dispatch('results/runSearch', page);
                    }
                    else {
                        throw Error;
                    }
                }).catch(error => {
                    context.commit('results/query/filters/resetFilters');
                });
            },
        }
    }
);

export default store;
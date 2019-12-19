import Vue from 'vue';
import Vuex from 'vuex';
import * as d3 from 'd3-collection';
import constants from './constants';
import results from './results';
import filters from './filters';

Vue.use(Vuex);

const store = new Vuex.Store(
    {
        state:     {
            search:      '',
            resourceIds: []
        },
        getters:   {
            query:           (state, getters) => {
                let q = {};
                if (state.search !== null && state.search !== '') {
                    q.search = state.search;
                }
                if (d3.values(state.filters.items).some((f) => f.parent !== null)) {
                    q.filters = getters['filters/queryfy']('group_root');
                }
                return q;
            },
            requestBody:     (state, getters) => {
                return {
                    query:        getters.query,
                    resource_ids: getters.sortedResources
                };
            },
            sortedResources: (state) => {
                return state.resourceIds.sort();
            },
            post:            () => (action, body) => {
                return fetch('/api/3/action/' + action, {
                    method:      'POST',
                    mode:        'cors',
                    cache:       'no-cache',
                    credentials: 'same-origin',
                    headers:     {
                        'Content-Type': 'application/json'
                    },
                    redirect:    'follow',
                    referrer:    'no-referrer',
                    body:        JSON.stringify(body)
                }).then(response => {
                    return response.json();
                });
            }
        },
        mutations: {
            setSearch(state, searchString) {
                state.search = searchString;
            },
            setResourceIds(state, resourceIds) {
                state.resourceIds = resourceIds;
            },
            selectAllResources(state) {
                let resourceIds = [];
                state.constants.packageList.forEach((pkg) => {
                    resourceIds = resourceIds.concat(pkg.resourceIds)
                });
                state.resourceIds = resourceIds;
            },
            togglePackageResources(state, packageIx) {
                let pkg           = state.constants.packageList[packageIx];
                let isInResources = pkg.resourceIds.some((r) => {
                    return state.resourceIds.includes(r);
                });
                if (isInResources) {
                    state.resourceIds = state.resourceIds.filter((resourceId) => {
                        return !pkg.resourceIds.includes(resourceId);
                    });
                }
                else {
                    state.resourceIds = state.resourceIds.concat(pkg.resourceIds.filter((x) => {
                        return !state.resourceIds.includes(x);
                    }));
                }
            },
        },
        actions:   {
            resolveSlug(context, slug) {
                if (slug === undefined || slug === '') {
                    context.commit('filters/resetFilters');
                    return;
                }
                context.getters.post('datastore_resolve_slug', {
                    slug: slug
                }).then(data => {
                    if (data.success) {
                        context.commit('setResourceIds', data.result.resource_ids);
                        if (data.result.query.search !== undefined) {
                            context.commit('setSearch', data.result.query.search)
                        }
                        context.commit('filters/setFromQuery', data.result.query);
                        context.dispatch('results/runSearch', 0);
                    }
                    else {
                        context.commit('filters/resetFilters');
                    }
                });
            },
            setHasImage(context) {
                let imageFields = [];

                context.state.resourceIds.map(r => {
                    return context.getters['constants/resourceDetails'][r].raw._image_field
                }).filter(f => {
                    return f !== null && f !== undefined && f !== 'None';
                }).forEach(f => {
                    if (!imageFields.includes(f)){
                        imageFields.push(f)
                    }
                });

                let newTerm = {
                    parent: 'group_root', key: 'exists', content: {
                        fields: imageFields
                    }, name: 'hasImage'
                };

                if (!context.getters['filters/hasTerm'](newTerm)) {
                    context.commit('filters/addTerm', newTerm);
                    context.dispatch('results/runSearch', 0);
                }
            }
        },
        modules:   {
            constants: constants,
            results:   results,
            filters:   filters
        }
    }
);

export default store;
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
            search:       '',
            resourceIds:  []
        },
        getters:   {
            query: (state, getters) => {
                let q = {
                    query_version: 'v1.0.0'
                };
                if (state.search !== null && state.search !== '') {
                    q.search = state.search;
                }
                if (d3.values(state.filters.items).some((f) => f.parent !== null)) {
                    q.filters = getters['filters/queryfy']('group_1');
                }
                return q;
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
                let pkg            = state.constants.packageList[packageIx];
                let isInResources  = pkg.resourceIds.some((r) => {
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
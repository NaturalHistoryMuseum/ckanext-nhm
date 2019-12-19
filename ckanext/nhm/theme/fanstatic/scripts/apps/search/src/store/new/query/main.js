import resources from './resources';
import filters from './filters';
import misc from './misc';
import * as d3 from 'd3-collection';
import Vue from 'vue';

let query = {
    namespaced: true,
    modules:    {
        resources,
        filters,
        misc
    },
    state: {
        requestBody: {
            query: {},
            resource_ids: []
        },
        parsingError: {
            unknown: false,
            resourceIds: null,
            queryBody: null
        }
    },
    actions: {
        setRequestBody(context, newBody) {
            if (newBody === null) {
                let q = {};
                if (context.state.search !== null && context.state.search !== '') {
                    q.search = context.state.search;
                }
                if (d3.values(context.state.filters.items).some((f) => f.parent !== null)) {
                    q.filters = context.getters.queryfy('group_root');
                }
                Vue.set(context.state.requestBody, 'query', q);
                Vue.set(context.state.requestBody, 'resource_ids', context.getters.sortedResources)
            }
            else {
                Vue.set(context.state.parsingError, 'resourceIds', context.getters.invalidResourceIds(newBody.resource_ids));
                if (context.state.parsingError.resourceIds === null) {
                    context.commit('setResourceIds', newBody.resource_ids);
                }
                else {
                    return;
                }
                context.commit('filters/setFromQuery', newBody.query || {});
                Vue.set(context.state.parsingError, 'queryBody', context.state.filters.parsingError);
                if (context.state.parsingError.queryBody !== null) {
                    return;
                }

                if (newBody.query !== undefined && newBody.query.search !== undefined){
                    Vue.set(context.state.requestBody.query, 'search', newBody.query.search.toString())
                }

                if (newBody.after !== undefined) {
                    Vue.set(context.state.requestBody, 'after', newBody.after)
                }
            }
        }
    }
};

export default query;
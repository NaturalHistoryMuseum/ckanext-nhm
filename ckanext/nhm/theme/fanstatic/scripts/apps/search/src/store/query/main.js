import resources from './resources';
import filters from './filters';
import Vue from 'vue';

let query = {
    namespaced: true,
    modules:    {
        resources,
        filters
    },
    state:      {
        search:       null,
        after:        null
    },
    getters:    {
        requestBody: (state, getters) => (ignoreTemp) => {
            ignoreTemp = ignoreTemp || false;
            let body = {
                query:        getters.queryBody(ignoreTemp),
                resource_ids: getters['resources/sortedResources']
            };

            if (state.after !== null && state.after !== undefined) {
                body.after = state.after;
            }

            return body;
        },
        queryBody:   (state, getters) => (ignoreTemp) => {
            ignoreTemp = ignoreTemp || false;
            let body   = {};
            if (state.search !== null && state.search !== '') {
                body.search = state.search;
            }

            if (getters['filters/count'](ignoreTemp) > 1) {
                body.filters = getters['filters/queryfy']('group_root', ignoreTemp)
            }
            return body;
        }
    },
    mutations:  {
        setSearch(state, searchString) {
            state.search = searchString;
        },
        setAfter(state, after) {
            state.after = after;
        }
    },
    actions:    {
        setRequestBody(context, newBody) {
            Vue.set(context.rootState.appState.query.parsingError, 'resourceIds', context.getters['resources/invalidResourceIds'](newBody.resource_ids));
            if (context.rootState.appState.query.parsingError.resourceIds === null) {
                context.commit('resources/setResourceIds', newBody.resource_ids);
            }
            else {
                return;
            }
            context.commit('filters/setFromQuery', newBody.query || {});
            Vue.set(context.rootState.appState.query.parsingError, 'queryBody', context.state.filters.parsingError);
            if (context.rootState.appState.query.parsingError.queryBody !== null) {
                return;
            }

            if (newBody.query !== undefined && newBody.query.search !== undefined) {
                context.state.search = newBody.query.search.toString();
            }

            if (newBody.after !== undefined) {
                context.state.after = newBody.after;
            }
        }
    }
};

export default query;
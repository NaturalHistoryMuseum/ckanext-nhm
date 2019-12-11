import * as d3 from 'd3-collection';
import Vue from 'vue';

let results = {
    namespaced: true,
    state:      {
        current:            {},
        view: 'Table',
        after:              [],
        page:               0,
        failed:             false,
        headers:            [],
        resultsLoading:     false,
        resultsInvalid:     false,
        slug:               null,
        slugLoading:        false,
        slugFailed:         false,
        doi:                null,
        doiLoading:         false,
        doiFailed:          false,
        download:           null,
        downloadProcessing: false,
        downloadFailed:     false
    },
    getters:    {
        hasResult:         (state) => {
            return state.current.success || false;
        },
        hasRecords:        (state, getters) => {
            let noRecords = getters.hasResult ? state.current.result.records.length === 0 : false;
            return getters.hasResult && !noRecords;
        },
        total:             (state, getters) => {
            return getters.hasResult ? state.current.result.total : 0;
        },
        records:           (state, getters) => {
            return getters.hasResult ? state.current.result.records : [];
        },
        resultResourceIds: (state, getters) => {
            return getters.records.map(r => r.resource);
        }
    },
    mutations:  {
        addPage(state, payload) {
            if (state.after.indexOf(payload.after) < 0) {
                state.after.push(payload.after);
            }
        },
        setPage(state, page) {
            state.page    = page;
            state.current = {};
        },
        setView(state, viewName) {
            state.view = viewName;
        },
        invalidateResults(state) {
            state.slug           = null;
            state.doi            = null;
            state.downloadId     = null;
            state.resultsInvalid = true;
        },
        addCustomHeader(state, field) {
            state.headers.push([field])
        },
        removeHeader(state, headerIndex) {
            Vue.delete(state.headers, headerIndex);
        },
        moveHeader(state, payload) {
            let header = state.headers[payload.ix];
            let target = state.headers[payload.ix + payload.by];
            Vue.set(state.headers, payload.ix + payload.by, header);
            Vue.set(state.headers, payload.ix, target);
        }
    },
    actions:    {
        runSearch(context, page) {
            context.state.resultsLoading = true;
            if (page === null || page === 0) {
                context.state.after = [];
            }
            context.commit('setPage', page);
            context.dispatch('getHeaders');

            let body = {...context.rootGetters.requestBody};
            if (context.state.page > 0) {
                body.after = context.state.after[context.state.page - 1];
            }
            context.rootGetters.post('datastore_multisearch', body).then(data => {
                context.state.current        = data;
                context.state.resultsLoading = false;
                if (data.success && data.result.after !== null) {
                    context.commit('addPage', {after: data.result.after});
                }
                context.state.failed         = !data.success;
                context.state.resultsInvalid = false;
            });
        },
        getSlug(context) {
            context.state.slugLoading = true;
            context.state.slugFailed  = false;
            context.rootGetters.post('datastore_create_slug', {
                query:        context.rootGetters.query,
                resource_ids: context.rootState.resourceIds
            }).then(data => {
                context.state.slugLoading = false;
                if (data.success) {
                    context.state.slug = data.result.slug;
                }
                else {
                    context.state.slug       = null;
                    context.state.slugFailed = true;
                }
            });
        },
        getDOI(context, payload) {
            if (payload.email_address === null) {
                return;
            }

            context.state.doiLoading = true;
            context.state.doiFailed  = false;

            payload.query        = context.rootGetters.query;
            payload.resource_ids = context.rootState.resourceIds;

            context.rootGetters.post('create_doi', payload).then(data => {
                context.state.doiLoading = false;
                console.log(data);
                if (data.success) {
                    context.state.doi = data.result.doi;
                }
                else {
                    context.state.doi       = null;
                    context.state.doiFailed = true;
                }
            });
        },
        getHeaders(context) {
            context.state.headers = [];

            d3.values(context.rootState.filters.items).forEach(f => {
                if (f.content.fields !== undefined) {
                    context.state.headers.push(f.content.fields)
                }
            });
            context.rootGetters.post('datastore_guess_fields', {
                query:        context.rootGetters.query,
                resource_ids: context.rootState.resourceIds
            }).then(data => {
                if (data.success) {
                    context.state.headers = context.state.headers.concat(data.result.map(f => d3.keys(f.fields)));
                }
            });

            context.state.headers = context.state.headers.filter(h => {
                return !context.state.headers.map(x => JSON.stringify(x))
                               .includes(JSON.stringify(h))
            });
        },
        requestDownload(context, payload) {
            if (payload.email_address === null) {
                return;
            }

            context.state.downloadProcessing = true;
            context.state.downloadFailed     = false;

            payload.query        = context.rootGetters.query;
            payload.resource_ids = context.rootState.resourceIds;

            context.rootGetters.post('datastore_queue_download', payload).then(data => {
                context.state.downloadProcessing = false;
                if (data.success) {
                    context.state.download = data.result;
                }
                else {
                    context.state.downloadFailed = true;
                }
            })
        }
    }
};

export default results;
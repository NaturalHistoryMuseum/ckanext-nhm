import display from './display';
import query from '../query/main';
import {post} from '../utils';
import Vue from 'vue';

let results = {
    // would rather not namespace this but there's a vuex bug with non-namespaced states
    namespaced: true,
    modules:    {
        display,
        query
    },
    state:      {
        invalidated:          false,
        resultData:           {},
        unfilteredResultData: {},
        slug:                 null,
        doi:                  null,
        download:             null,
        after:                [],
        page:                 0,
        status:               {
            resultData: {
                loading: false,
                failed:  false
            },
            slug:       {
                loading: false,
                failed:  false
            },
            doi:        {
                loading: false,
                failed:  false
            },
            download:   {
                loading: false,
                failed:  false
            }
        }
    },
    getters:    {
        hasResult:         (state) => {
            return state.resultData.success || false;
        },
        hasRecords:        (state, getters) => {
            let noRecords = getters.hasResult ? state.resultData.result.records.length === 0 : false;
            return getters.hasResult && !noRecords;
        },
        total:             (state, getters) => {
            return getters.hasResult ? state.resultData.result.total : 0;
        },
        records:           (state, getters) => {
            return getters.hasResult ? state.resultData.result.records : [];
        },
        resultResourceIds: (state, getters) => {
            return getters.records.map(r => r.resource);
        },
        unfilteredTotal:   (state, getters) => {
            if (state.unfilteredResultData.success) {
                return state.unfilteredResultData.result.total;
            }
            else if (getters.hasResult) {
                return getters.total;
            }
            else {
                return 0;
            }
        }
    },
    mutations:  {
        addPage(state, after) {
            if (state.after.indexOf(after) < 0) {
                state.after.push(after);
            }
        },
        setPage(state, page) {
            state.page       = page;
            state.resultData = {};
        },
    },
    actions:    {
        runSearch(context, page) {
            page = page || 0;
            Vue.set(context.state.status.resultData, 'loading', true);
            if (page === 0) {
                context.state.after = [];
            }
            context.commit('setPage', page);
            context.dispatch('display/getHeaders', {
                filters: context.state.query.filters.items,
                request: context.getters['query/requestBody'](false)
            });

            context.commit('query/setAfter', context.state.after[context.state.page - 1]);

            let tempFilters = context.getters['query/filters/temporaryFilters'];

            post('datastore_multisearch', context.getters['query/requestBody'](false))
                .then(data => {
                    context.state.resultData = data;
                    Vue.set(context.state.status.resultData, 'loading', false);
                    if (data.success && data.result.after !== null) {
                        context.commit('addPage', data.result.after);
                    }
                    Vue.set(context.state.status.resultData, 'failed', !data.success);
                    context.state.invalidated = false;

                    if (tempFilters.length === 0) {
                        context.state.unfilteredResultData = data;
                    }
                });

            if (tempFilters.length > 0) {
                post('datastore_multisearch', context.getters['query/requestBody'](true))
                    .then(data => {
                        context.state.unfilteredResultData = data;
                    });
            }
        },
        getMetadata(context, payload) {
            Vue.set(context.state.status[payload.meta], 'loading', true);
            Vue.set(context.state.status[payload.meta], 'failed', false);

            let body = context.getters['query/requestBody'](false);
            if (payload.formData !== undefined) {
                body = $.extend(payload.formData);
            }

            post(payload.action, body)
                .then(data => {
                    Vue.set(context.state.status[payload.meta], 'loading', false);
                    if (data.success) {
                        context.state[payload.meta] = payload.extract(data);
                    }
                    else {
                        context.state[payload.meta] = null;
                        Vue.set(context.state.status[payload.meta], 'failed', true);
                    }
                });
        },
        getSlug(context) {
            context.dispatch('getMetadata', {
                meta:    'slug',
                action:  'datastore_create_slug',
                extract: (data) => data.result.slug
            });
        },
        getDOI(context, payload) {
            if (payload.email_address === null) {
                return;
            }

            context.dispatch('getMetadata', {
                meta:     'doi',
                action:   'create_doi',
                formData: payload,
                extract:  (data) => data.result.doi
            });
        },
        getDownload(context, payload) {
            if (payload.email_address === null) {
                return;
            }

            context.dispatch('getMetadata', {
                meta:     'download',
                action:   'datastore_queue_download',
                formData: payload,
                extract:  (data) => data.result
            });
        },
        reset(context) {
            context.commit('query/setSearch', null);
            context.commit('query/setAfter', null);
            context.commit('query/filters/resetFilters');
            context.commit('query/resources/selectAllResources');
            context.dispatch('invalidate');
        },
        invalidate(context) {
            context.state.invalidated = true;
            context.state.slug        = null;
            context.state.doi         = null;
            context.state.download    = null;
        }
    }
};

export default results
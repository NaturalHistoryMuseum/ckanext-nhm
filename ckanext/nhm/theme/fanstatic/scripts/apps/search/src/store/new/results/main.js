import display from './display';
import query from '../query/main';
import {post} from '../utils';
import Vue from 'vue';

let results = {
    namespaced: false,
    modules:    {
        display,
        query
    },
    state:      {
        invalidated: false,
        data:        {},
        slug:        null,
        doi:         null,
        download:    null,
        after:       [],
        page:        0,
        status:      {
            data:     {
                loading: false,
                failed:  false
            },
            slug:     {
                loading: false,
                failed:  false
            },
            doi:      {
                loading: false,
                failed:  false
            },
            download: {
                loading: false,
                failed:  false
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
            state.page = page;
            state.data = {};
        },
    },
    actions:    {
        runSearch(context, page) {
            Vue.set(context.state.status.data, 'loading', true);
            if (page === null || page === 0) {
                context.state.after = [];
            }
            context.commit('setPage', page);
            context.dispatch('display/getHeaders', {
                filters: context.state.query.filters.items,
                request: context.state.requestBody
            });

            let body = {...context.state.query.requestBody};
            if (context.state.page > 0) {
                body.after = context.state.after[context.state.page - 1];
            }
            post('datastore_multisearch', body)
                .then(data => {
                    context.state.data = data;
                    Vue.set(context.state.status.data, 'loading', false);
                    if (data.success && data.result.after !== null) {
                        context.commit('addPage', data.result.after);
                    }
                    Vue.set(context.state.status.data, 'failed', !data.success);
                    context.state.invalidated = false;
                });

            context.dispatch('query/setRequestBody', body);
        },
        getSlug(context) {
            Vue.set(context.state.status.slug, 'loading', true);
            Vue.set(context.state.status.slug, 'failed', false);
            post('datastore_create_slug', context.state.query.requestBody)
                .then(data => {
                    Vue.set(context.state.status.slug, 'loading', false);
                    if (data.success) {
                        context.state.slug = data.result.slug;
                    }
                    else {
                        context.state.slug = null;
                        Vue.set(context.state.status.slug, 'failed', true);
                    }
                });
        },
        getDOI(context, payload) {
            if (payload.email_address === null) {
                return;
            }

            Vue.set(context.state.status.doi, 'loading', true);
            Vue.set(context.state.status.doi, 'failed', false);

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
    }
};

export default results
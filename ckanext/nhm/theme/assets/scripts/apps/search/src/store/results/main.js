import display from './display';
import query from '../query/main';
import images from './images';
import {post} from '../utils';
import Vue from 'vue';
import pako from 'pako';

let results = {
    // would rather not namespace this but there's a vuex bug with non-namespaced states
    namespaced: true,
    modules:    {
        display,
        query,
        images
    },
    state:      {
        invalidated:     false,
        resultData:      {},
        unfilteredTotal: 0,
        slug:            null,
        slugReserved:    false,
        doi:             null,
        download:        null,
        queryParams:     null,
        _after:          [],
        page:            0,
        downloadId:      null
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
        imageRecords:      (state, getters) => {
            let imgRecords = [];

            getters.records.forEach((r, rix) => {
                getters['images/getItemImages'](r, false, rix).forEach((i) => {
                    imgRecords.push(i)
                })
            });

            return imgRecords;
        },
        loadedImageRecords: (state, getters) => {
            return getters.imageRecords.filter(r => !r.image.isBroken);
        },
        resultResourceIds: (state, getters) => {
            return getters.records.map(r => r.resource);
        },
        pageParam:         (state) => {
            function compressString(arr) {
                let str                = JSON.stringify(arr);
                let compressedString   = Buffer.from(pako.deflate(str, {to: 'array'}))
                                               .toString('base64');
                let decompressedString = pako.inflate(Buffer.from(compressedString, 'base64'), {to: 'string'});
                if (str !== decompressedString) {
                    console.error(decompressedString);
                    if (arr.length === 1) {
                        return '';
                    }
                    else {
                        return compressString(arr.slice(0, arr.length - 1))
                    }
                }
                return compressedString;
            }

            return compressString(state._after.slice(0, state.page + 1));
        },
        after:             (state, getters) => {
            return state._after.map(a => {
                return [a[0], a[1], getters['query/resources/sortedResources'][a[2]]]
            })
        }
    },
    mutations:  {
        addPage(state, after) {
            if (state._after.indexOf(after) < 0) {
                state._after.push(after);
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
            Vue.set(context.rootState.appState.status.resultData, 'loading', true);
            Vue.set(context.rootState.appState.status.resultData, 'failed', false);
            if (page === 0) {
                context.state._after = [];
                // only get the headers on first page, subsequent pages just use the same headers
                context.dispatch('display/getHeaders', {
                    filters: context.state.query.filters.items,
                    request: context.getters['query/requestBody'](false)
                });
            }
            context.commit('setPage', page);
            context.commit('query/setAfter', context.getters.after[context.state.page - 1]);

            let tempFilters = context.getters['query/filters/temporaryFilters'];

            post('datastore_multisearch', context.getters['query/requestBody'](false))
                .then(data => {
                    context.state.resultData = data;

                    if (data.success && data.result.after !== null) {
                        let afterToAdd = [data.result.after[0], data.result.after[1], context.getters['query/resources/sortedResources']
                            .indexOf(data.result.after[2].replace('nhm-', ''))]
                        context.commit('addPage', afterToAdd);
                    }
                    if (!data.success) {
                        throw Error;
                    }

                    if (tempFilters.length === 0) {
                        if (data.success) {
                            context.state.unfilteredTotal = data.result.total;
                        }
                        else {
                            context.state.unfilteredTotal = 0;
                        }
                    }
                })
                .catch(error => {
                    Vue.set(context.rootState.appState.status.resultData, 'failed', true);
                })
                .finally(() => {
                    Vue.set(context.rootState.appState.status.resultData, 'loading', false);
                    context.state.invalidated = false;
                });

            if (tempFilters.length > 0) {
                post('datastore_multisearch', context.getters['query/requestBody'](true))
                    .then(data => {
                        if (data.success) {
                            context.state.unfilteredTotal = data.result.total;
                        }
                        else {
                            throw Error;
                        }
                    })
                    .catch(error => {
                        if (context.getters.hasResult) {
                            context.state.unfilteredTotal = context.getters.total;
                        }
                        else {
                            context.state.unfilteredTotal = 0;
                        }
                    });
            }
        },
        getMetadata(context, payload) {
            Vue.set(context.rootState.appState.status[payload.meta], 'loading', true);
            Vue.set(context.rootState.appState.status[payload.meta], 'failed', false);

            let body = context.getters['query/requestBody'](false);
            if (payload.formData !== undefined) {
                body = Object.assign(body, payload.formData);
            }

            post(payload.action, body)
                .then(data => {
                    if (data.success) {
                        context.state[payload.meta] = payload.extract(data);
                    }
                    else {
                        throw Error;
                    }
                })
                .catch(error => {
                    context.state[payload.meta] = null;
                    Vue.set(context.rootState.appState.status[payload.meta], 'failed', true);
                })
                .finally(() => {
                    Vue.set(context.rootState.appState.status[payload.meta], 'loading', false);
                });
        },
        getSlug(context) {
            context.dispatch('getMetadata', {
                meta:    'slug',
                action:  'datastore_create_slug',
                extract: (data) => {
                    Vue.set(context.state, 'slugReserved', data.result.is_reserved);
                    return data.result.slug;
                }
            });
        },
        editSlug(context, payload) {
            Vue.set(context.rootState.appState.status.slugEdit, 'loading', true)
            return post('datastore_edit_slug', {
                current_slug: context.state.slug,
                new_reserved_slug: payload
            }).then(d => {
                Vue.set(context.rootState.appState.status.slugEdit, 'failed', !d.success)
                if (d.success) {
                    context.dispatch('getSlug');
                }
            }).catch(e => {
                Vue.set(context.rootState.appState.status.slugEdit, 'failed', true);
            }).finally(() => {
                Vue.set(context.rootState.appState.status.slugEdit, 'loading', false)
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
            payload['query'] = context.getters['query/requestBody']();
            context.dispatch('getMetadata', {
                meta:     'download',
                action:   'datastore_queue_download',
                formData: payload,
                extract:  (data) => {
                    if (data.success) {
                        Vue.set(context.state, 'downloadId', data.result.download_id);
                    }
                    else {
                        Vue.set(context.state, 'downloadId', null);
                    }
                    return data.result;
                }
            });
        },
        resetDownload(context) {
            Vue.set(context.state, 'downloadId', null);
            Vue.set(context.state, 'download', null);
        },
        reset(context) {
            context.commit('query/setSearch', null);
            context.commit('query/setAfter', null);
            context.commit('query/filters/resetFilters');
            context.commit('query/resources/selectAllResources');
            context.commit('display/setView', 'Table')
            context.state.resultData = {}
            Vue.set(context.rootState.appState.status.resultData, 'loading', false);
            Vue.set(context.rootState.appState.status.resultData, 'failed', false);
            context.dispatch('resetDownload');
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

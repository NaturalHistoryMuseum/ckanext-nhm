let results = {
    namespaced: true,
    state:      {
        current:        {},
        after:          [],
        page:           0,
        slug:           null,
        failed:         false,
        slugLoading:    false,
        resultsLoading: false,
        resultsInvalid: false
    },
    getters:    {
        requestBody: (state, getters, rootState, rootGetters) => {
            let body = {
                query:        rootGetters.query,
                resource_ids: rootState.resourceIds
            };
            if (state.page > 0) {
                body.after = state.after[state.page - 1];
            }
            return JSON.stringify(body);
        },
        hasResult:   (state) => {
            return state.current.success || false;
        },
        hasRecords:  (state, getters) => {
            let noRecords = getters.hasResult ? state.current.result.records.length === 0 : false;
            return getters.hasResult && !noRecords;
        },
        total:       (state, getters) => {
            return getters.hasResult ? state.current.result.total : 0;
        },
        records:     (state, getters) => {
            return getters.hasResult ? state.current.result.records : [];
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
        invalidateResults(state) {
            state.slug = null;
            state.resultsInvalid = true;
        }
    },
    actions:    {
        runSearch(context, page) {
            context.state.resultsLoading = true;
            context.state.resultsInvalid = false;
            if (page === null || page === 0) {
                context.state.after = [];
            }
            context.commit('setPage', page);
            fetch('/api/3/action/datastore_multisearch', {
                method:      'POST',
                mode:        'cors',
                cache:       'no-cache',
                credentials: 'same-origin',
                headers:     {
                    'Content-Type': 'application/json'
                },
                redirect:    'follow',
                referrer:    'no-referrer',
                body:        context.getters.requestBody,
            }).then(response => {
                return response.json();
            }).then(data => {
                context.state.current        = data;
                context.state.resultsLoading = false;
                if (data.success && data.result.after !== null) {
                    context.commit('addPage', {after: data.result.after});
                    context.state.failed = false;
                }
                else if (!data.success) {
                    context.state.failed = true;
                }
            });
        },
        getSlug(context) {
            context.state.slugLoading = true;
            fetch('/api/3/action/datastore_create_slug', {
                method:      'POST',
                mode:        'cors',
                cache:       'no-cache',
                credentials: 'same-origin',
                headers:     {
                    'Content-Type': 'application/json'
                },
                redirect:    'follow',
                referrer:    'no-referrer',
                body:        JSON.stringify({
                                                query:        context.rootGetters.query,
                                                resource_ids: context.rootState.resourceIds
                                            }),
            }).then(response => {
                return response.json();
            }).then(data => {
                context.state.slugLoading = false;
                if (data.success) {
                    context.state.slug = data.result.slug;
                }
                else {
                    context.state.slug = null;
                }
            });
        }
    }
};

export default results;
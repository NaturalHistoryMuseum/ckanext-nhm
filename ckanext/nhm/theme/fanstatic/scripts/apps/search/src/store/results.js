let results = {
    namespaced: true,
    state:      {
        current: {},
        after:   [],
        page:    0,
        slug: null
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
        success:     (state) => {
            let successful = state.current.success || false;
            let noRecords  = successful ? state.current.result.records.length === 0 : false;
            return successful && !noRecords;
        },
        total:       (state, getters) => {
            return getters.success ? state.current.result.total : 0;
        },
        records:     (state, getters) => {
            return getters.success ? state.current.result.records : [];
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
        invalidateSlug(state) {
            state.slug = null;
        }
    },
    actions:    {
        runSearch(context, page) {
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
                context.state.current = data;
                if (data.success && data.result.after !== null) {
                    context.commit('addPage', {after: data.result.after})
                }
                else if (!data.success) {
                    console.error(data);
                    console.error(context.getters.requestBody);
                }
            });
        },
        getSlug(context) {
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
                body:        JSON.stringify({
                                                query:        context.rootGetters.query,
                                                resource_ids: context.rootState.resourceIds
                                            }),
            }).then(response => {
                return response.json();
            }).then(data => {
                context.state.slug = data.slug;
            });
        }
    }
};

export default results;
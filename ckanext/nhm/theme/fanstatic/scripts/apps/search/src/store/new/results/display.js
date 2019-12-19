import Vue from 'vue';
import * as d3 from 'd3-collection';
import {post} from '../utils';

let display = {
    namespaced: true,
    state:      {
        view:    'Table',
        headers: [],
    },
    mutations:  {
        setView(state, viewName) {
            state.view = viewName;
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
        getHeaders(context, payload) {
            context.state.headers = [];

            d3.values(payload.filters).forEach(f => {
                if (f.content.fields !== undefined) {
                    context.state.headers.push(f.content.fields)
                }
            });
            post('datastore_guess_fields', payload.request)
                .then(data => {
                    if (data.success) {
                        context.state.headers = context.state.headers.concat(data.result.map(f => d3.keys(f.fields)));
                    }
                });

            context.state.headers = context.state.headers.filter(h => {
                return !context.state.headers.map(x => JSON.stringify(x))
                               .includes(JSON.stringify(h))
            });
        },
    }
};

export default display;
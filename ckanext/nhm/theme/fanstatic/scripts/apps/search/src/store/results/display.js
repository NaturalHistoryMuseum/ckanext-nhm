import Vue from 'vue';
import * as d3 from 'd3-collection';
import {post} from '../utils';

let display = {
    namespaced: true,
    state:      {
        view:             'Table',
        headers:          [],
        viewerImageIndex: 0,
        viewerImagePage:  [],
        showImage:        false,
        recordName:       'record$'  // replace $ with s to make plural
    },
    getters:    {
        viewerImage:  (state) => {
            return state.viewerImagePage[state.viewerImageIndex];
        },
        recordHeader: (state) => (recordCount) => {
            return `${recordCount.toLocaleString('en-GB')} ${state.recordName.replace('$', recordCount === 1 ? '' : 's')}`
        }
    },
    mutations:  {
        setView(state, viewName) {
            state.view = viewName;
        },
        setViewerImage(state, imageIndex) {
            state.viewerImageIndex = imageIndex;
            state.showImage        = true;
        },
        addPageImages(state, images) {
            state.viewerImagePage = images;
        },
        hideImage(state) {
            state.showImage   = false;
            state.viewerImage = 0;
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
            let headers           = [];

            d3.values(payload.filters).forEach(f => {
                if (f.content.fields !== undefined) {
                    headers.push(f.content.fields)
                }
            });

            post('datastore_guess_fields', payload.request)
                .then(data => {
                    if (data.success) {
                        headers = headers.concat(data.result.map(f => d3.keys(f.fields)));
                        headers.forEach(h => {
                            if (!context.state.headers.map(x => JSON.stringify(x))
                                        .includes(JSON.stringify(h))) {
                                context.state.headers.push(h)
                            }
                        });
                    }
                });
        },
    }
};

export default display;
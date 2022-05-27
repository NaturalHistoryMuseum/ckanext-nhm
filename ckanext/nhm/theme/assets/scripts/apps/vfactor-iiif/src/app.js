import Vue from 'vue';
import App from './App.vue';
import Vuex from 'vuex';
import {SET_QUERY, SET_RECORD} from './mutation-types';
import {API} from "./api";

const rootElement = document.getElementById('vfactor-iiif-app');
const resourceId = rootElement.getAttribute('data-resource-id')

Vue.use(Vuex);

const store = new Vuex.Store({
    state: {
        resourceId: resourceId,
        query: {},
        record: null
    },
    mutations: {
        [SET_RECORD](state, newRecord) {
            state.record = newRecord;
        }
        ,
        [SET_QUERY](state, newQuery) {
            state.query = newQuery;
        }
    }
});

export const api = new API(store.state);

const app = new Vue({
    el: '#vfactor-iiif-app',
    store,
    template: '<App/>',
    components: {App}
});

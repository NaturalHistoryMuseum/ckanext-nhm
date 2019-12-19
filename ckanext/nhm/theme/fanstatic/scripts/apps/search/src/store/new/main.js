import Vue from 'vue';
import Vuex from 'vuex';
import results from './results/main';

Vue.use(Vuex);

const store = new Vuex.Store(
    {
        modules:   {
            results
        },
        state:     {
            appLoading: false,
            appError:   false
        },
        getters:   {
            getGroup: state => groupId => {
                return {
                    'and': 'ALL OF',
                    'or':  'ANY OF',
                    'not': 'NONE OF'
                }[groupId];
            },
        },
        mutations: {},
        actions:   {}
    }
);

export default store;
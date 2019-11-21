import Vue from 'vue';
import App from './App.vue';
import store from './store/main';


new Vue({
            el:     '#searchApp',
            store,
            render: h => h(App),
        });
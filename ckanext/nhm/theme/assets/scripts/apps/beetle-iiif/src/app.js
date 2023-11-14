import Vue from 'vue';
import App from './App.vue';
import store from './store';
import { API } from './api';

export const api = new API(store.state);

const app = new Vue({
  el: '#beetle-iiif-app',
  store,
  template: '<App/>',
  components: { App },
});

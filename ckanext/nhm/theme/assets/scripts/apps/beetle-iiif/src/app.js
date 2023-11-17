import Vue from 'vue';
import App from './App.vue';
import store from './store';

const app = new Vue({
  el: '#beetle-iiif-app',
  store,
  template: '<App/>',
  components: { App },
});

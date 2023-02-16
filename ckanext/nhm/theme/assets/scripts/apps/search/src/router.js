import App from './App.vue';
import VueRouter from 'vue-router';

const routes = [{ path: '/search/:slug*', component: App }];
const router = new VueRouter({
  routes,
  mode: 'history',
});

export default router;

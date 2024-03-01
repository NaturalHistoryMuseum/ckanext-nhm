import Results from '../components/Results.vue';
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', component: Results },
  { path: '/:mode*', component: Results },
];

const router = createRouter({
  routes,
  history: createWebHistory('/image-viewer/'),
});

export default router;

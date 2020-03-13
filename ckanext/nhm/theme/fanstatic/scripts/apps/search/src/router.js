import App from './App.vue';
import VueRouter from 'vue-router';

const routes = [
    {path: '/search', component: App},
    {path: '/search/:slug', component: App}
]
const router = new VueRouter({
                                 routes,
                                 mode: 'history'
                             })


export default router;
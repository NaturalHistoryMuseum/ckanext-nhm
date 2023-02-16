import Vue from 'vue';
import VueRouter from 'vue-router';
import VueClipboard from 'vue-clipboard2';
import store from './store/main';
import router from './router';
import 'core-js/stable';
import 'regenerator-runtime/runtime';

// for bundling purposes
require('leaflet/dist/leaflet.css');

// bundle leaflet images
function importFolder(context) {
  context.keys().forEach(context);
}

importFolder(
  require.context('leaflet/dist/images/', true, /\.(png|jpe?g|gif)$/i),
);

// plugins
Vue.use(VueClipboard);
Vue.use(VueRouter);

// directives
let outsideClick = {};
Vue.directive('dismiss', {
  bind(el, binding, vnode) {
    outsideClick[vnode.context._uid] = (event) => {
      event.stopPropagation();
      if (!$.contains(el, event.target)) {
        let ignore = binding.value.ignore.some((selector) =>
          event.target.matches(selector),
        );
        let i = 0;
        while (!ignore && i < binding.value.ignore.length) {
          let parentNode = $(binding.value.ignore[i])[0];
          if (parentNode !== undefined) {
            ignore = $.contains(parentNode, event.target);
          }
          i++;
        }
        if (!ignore) {
          vnode.context[binding.value.switch] = false;
        }
      }
    };
    document.addEventListener('click', outsideClick[vnode.context._uid]);
    document.addEventListener('touchStart', outsideClick[vnode.context._uid]);
  },

  unbind(el, binding, vnode) {
    document.removeEventListener('click', outsideClick[vnode.context._uid]);
    document.removeEventListener(
      'touchstart',
      outsideClick[vnode.context._uid],
    );
  },
});

// routes
const RouterWrapper = { template: '<router-view></router-view>' };

// app
new Vue({
  el: '#searchApp',
  store,
  render: (createElement) => createElement(RouterWrapper),
  router,
});

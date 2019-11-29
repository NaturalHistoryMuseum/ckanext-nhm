import Vue from 'vue';
import App from './App.vue';
import store from './store/main';

let outsideClick;

Vue.directive('dismiss', {
    bind(el, binding, vnode) {
        outsideClick = (event) => {
            event.stopPropagation();
            if (!el.contains(event.target)) {
                let ignore = binding.value.ignore.includes(event.target.id);
                let i      = 0;
                while (!ignore && i < binding.value.ignore.length) {
                    let parentNode = $('#' + binding.value.ignore[i])[0];
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
        document.addEventListener('click', outsideClick);
        document.addEventListener('touchStart', outsideClick);
    },

    unbind() {
        document.removeEventListener('click', outsideClick);
        document.removeEventListener('touchstart', outsideClick);
    }
});

new Vue({
            el:      '#searchApp',
            store,
            created: function () {
                this.$store.dispatch('resolveSlug', $(this.$options.el).data('slug'));
            },
            render:  createElement => createElement(App),
        });
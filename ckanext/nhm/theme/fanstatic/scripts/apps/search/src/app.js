import Vue from 'vue';
import App from './App.vue';
import store from './store/main';

new Vue({
            el:     '#searchApp',
            store,
            created: function() {
                this.$store.dispatch('resolveSlug', $(this.$options.el).data('slug'));
            },
            render: createElement => createElement(App),
        });
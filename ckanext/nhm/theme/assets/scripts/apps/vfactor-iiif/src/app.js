import Vue from 'vue';
import App from './App.vue'

const rootElement = document.getElementById('vfactor-iiif-app');
const resourceId = rootElement.getAttribute('data-resource-id')

new Vue({
    el: '#vfactor-iiif-app',
    data: {
        resourceId
    },
    template: '<App :resource-id="resourceId"/>',
    components: {App}
});

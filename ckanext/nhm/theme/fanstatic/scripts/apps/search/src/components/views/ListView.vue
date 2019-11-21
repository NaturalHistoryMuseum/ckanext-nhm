<template>
    <div class="flex-container flex-column">
        <div v-for="item in records" :key="item.id">
        </div>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';
    import * as d3 from 'd3-collection';

    export default {
        extends:  BaseView,
        name:     'TableView',
        data:     function () {
            return {
                customHeaders: [],
                headers:       []
            }
        },
        computed: {
            allHeaders() {
                return this.headers.concat(this.customHeaders.map(h => [h]))
            }
        },
        methods:  {
            getHeaders() {
                let fields = [['_id']];

                d3.values(this.$store.state.filters.items).forEach(f => {
                    if (f.content.fields !== undefined) {
                        fields.push(f.content.fields)
                    }
                });

                this.headers = fields;
            },
            addNewColumn(field) {
                this.customHeaders.push(field);
            },
            deleteHeader(index) {
                this.$delete(this.customHeaders, index);
            },
            updateView() {
                this.getHeaders();
                this.getFieldList();
            }
        }
    }
</script>
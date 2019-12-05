<template>
    <div class="space-children-v field-picker" :class="classes">
        <input type="text" class="full-width" name="fieldSearch"
            id="fieldSearch"
            value="" autocomplete="off" placeholder="field name"
            v-model="fieldSearch"/>
        <select class="full-width" size="10">
            <option v-for="field in fieldList" v-bind:key="field.id"
                @click="callback(field)">{{ field }}
            </option>
        </select>
    </div>
</template>

<script>
    import {mapState} from 'vuex';

    export default {
        name:    'FieldPicker',
        data:    function () {
            return {
                fieldSearch: null,
                fieldList:   []
            }
        },
        props:   ['callback', 'resourceIds', 'classes'],
        computed: {
            ...mapState('results', ['current']),
        },
        methods: {
            getFieldList() {
                const vue = this;
                fetch('/api/3/action/datastore_field_autocomplete', {
                    method:      'POST',
                    mode:        'cors',
                    cache:       'no-cache',
                    credentials: 'same-origin',
                    headers:     {
                        'Content-Type': 'application/json'
                    },
                    redirect:    'follow',
                    referrer:    'no-referrer',
                    body:        JSON.stringify({
                                                    resource_ids: vue.resourceIds,
                                                    text:         vue.fieldSearch,
                                                    lowercase:    true
                                                }),
                }).then(response => {
                    return response.json();
                }).then(data => {
                    vue.fieldList = Object.keys(data.result.fields).sort();
                });
            },
        },
        mounted:  function () {
            this.getFieldList();
        },
        watch:   {
            fieldSearch() {
                this.getFieldList();
            },
            current: {
                handler() {
                    this.getFieldList();
                },
                deep: true
            }
        }
    }
</script>
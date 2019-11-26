<template>
    <pre>
        {{ $store.state.results.current.result }}
    </pre>
</template>

<script>
    import {mapGetters, mapState} from 'vuex';
    import * as d3 from 'd3-collection';

    export default {
        name:     'BaseView',
        data:     function () {
            return {
                showFields:    false,
                fieldSearch:   null,
                fieldList:     [],
                customHeaders: [],
                headers:       []
            }
        },
        mounted:  function () {
            this.updateView();
        },
        computed: {
            ...mapState('results', ['current']),
            ...mapGetters('constants', ['resourceDetails']),
            ...mapGetters('results', ['total', 'records']),
            allHeaders() {
                return this.headers.concat(this.customHeaders.map(h => [h]))
            }
        },
        methods:  {
            getFieldList() {
                const vue       = this;
                let resourceIds = this.current.result === undefined ? [] : this.current.result.records.map(r => r.resource);
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
                                                    resource_ids: resourceIds,
                                                    text:         vue.fieldSearch,
                                                    lowercase:    true
                                                }),
                }).then(response => {
                    return response.json();
                }).then(data => {
                    vue.fieldList = Object.keys(data.result.fields).sort();
                });
            },
            getUrls(resourceId) {
                let resDetails = this.resourceDetails[resourceId];

                let packageUrl  = `/dataset/${resDetails.package_id}`;
                let resourceUrl = packageUrl + `/resource/${resDetails.id}`;

                return {
                    packageUrl,
                    resourceUrl,
                    resourceName: resDetails.name
                }
            },
            getHeaders() {
                let fields = [];

                d3.values(this.$store.state.filters.items).forEach(f => {
                    if (f.content.fields !== undefined) {
                        fields.push(f.content.fields)
                    }
                });

                this.headers = fields;
            },
            addHeader(field) {
                this.customHeaders.push(field);
            },
            deleteHeader(index) {
                this.$delete(this.customHeaders, index);
            },
            updateView() {
                this.getHeaders();
                this.getFieldList();
            }
        },
        watch:    {
            current: {
                handler() {
                    this.updateView();
                },
                deep: true
            },
            fieldSearch() {
                this.getFieldList();
            }
        }
    }
</script>
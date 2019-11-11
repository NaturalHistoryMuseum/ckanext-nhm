<template>
    <div id="result">
        <h3>{{ total }} records</h3>
        <table class="table table-chunky" style="overflow-x: scroll" v-if="success">
            <thead>
            <tr>
                <th>Resource ID</th>
                <th v-for="headerGroup in headers" :key="headerGroup.id">
                    <span v-for="header in headerGroup" :key="header.id" class="term-group">
                        {{ header }}
                    </span>
                </th>
                <th v-for="(header, index) in customHeaders" :key="header.id">
                    {{ header }}
                    <i class="delete-field fas fa-times-circle fa-xs"
                        @click="deleteHeader(index)"></i>
                </th>
                <th>
                    <a href="#" @click="showFields = !showFields">
                        <i class="fas fa-plus-circle"></i>
                    </a>
                    <transition name="slidedown">
                        <div class="floating space-children-v term-editor-fields" v-if="showFields">
                            <input type="text" class="full-width" name="fieldSearch"
                                id="fieldSearch"
                                value="" autocomplete="off" placeholder="field name"
                                v-model="fieldSearch"/>
                            <select class="full-width" size="10">
                                <option v-for="field in fieldList" v-bind:key="field.id"
                                    @dblclick="addNewColumn(field)">{{ field }}
                                </option>
                            </select>
                        </div>
                    </transition>
                </th>
            </tr>
            </thead>

            <tr v-for="item in records" :key="item.id">
                <td>{{ item.resource }}</td>
                <td v-for="headerGroup in allHeaders" :key="headerGroup.id">
                    <span v-for="header in headerGroup" :key="header.id" class="term-group">
                        {{ item.data[header] || '--' }}
                    </span>
                </td>
                <td></td>
            </tr>
        </table>
    </div>
</template>

<script>
    export default {
        name:     'Results',
        data:     function () {
            return {
                customHeaders: [],
                headers:       [],
                showFields:    false,
                fieldSearch:   null,
                fieldList:     []
            }
        },
        mounted:  function () {
            this.getFieldList();
        },
        computed: {
            result:  function () {
                return this.$parent.result.result;
            },
            success: function () {
                let successful = this.$parent.result.success || false;
                let noRecords  = successful ? this.result.records.length === 0 : false;
                return successful && !noRecords;
            },
            total:   function () {
                return this.success ? this.result.total : 0;
            },
            records: function () {
                return this.success ? this.result.records : [];
            },
            allHeaders: function () {
                return this.headers.concat(this.customHeaders.map(h => [h]))
            }
        },
        methods:  {
            getHeaders:   function () {
                let fields = [['_id']];

                let getFields = (i) => {
                    let f = [];
                    if (i.fields === undefined) {
                        d3.values(i).map((v) => getFields(v)).forEach((v) => {
                            f = f.concat(v);
                        });
                    }
                    else {
                        f = [i.fields];
                    }
                    return f;
                };

                if (this.$parent.query.filters !== undefined) {
                    fields = fields.concat(getFields(this.$parent.query.filters));
                }

                this.headers = fields;
            },
            getFieldList: function () {
                const vue       = this;
                let resourceIds = this.result === undefined ? [] : d3.keys(this.result.resources);
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
                                                    prefix:       vue.fieldSearch,
                                                    lowercase:    true
                                                }),
                }).then(response => {
                    return response.json();
                }).then(data => {
                    vue.fieldList = Object.keys(data.result.fields).sort();
                });
            },
            addNewColumn: function (field) {
                this.customHeaders.push(field);
            },
            deleteHeader: function (index) {
                this.$delete(this.customHeaders, index);
            }
        },
        watch:    {
            result:      function () {
                console.log(this.result);
                this.getHeaders();
                this.getFieldList();
            },
            fieldSearch: function () {
                this.getFieldList();
            }
        }
    }
</script>
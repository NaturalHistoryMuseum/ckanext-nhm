<template>
    <div class="term-editor floating flex-container flex-nowrap flex-stretch-height">
        <i class="fas fa-caret-square-left" @click="closeDialog"></i>
        <div class="term-editor-fields space-children-v">
            <div class="flex-container flex-wrap flex-wrap-spacing">
                            <span class="fields" v-for="(field, index) in newFields"
                                v-bind:key="field.id">
                                {{ field }}
                                <i class="delete-field fas fa-times-circle fa-xs"
                                    @click="deleteField(index)"></i>
                            </span>
            </div>
            <input type="text" class="full-width" name="fieldSearch"
                id="fieldSearch"
                value="" autocomplete="off" placeholder="field name"
                v-model="fieldSearch" @keyup.enter="addNewField(fieldSearch)"/>
            <select class="full-width" size="10">
                <option v-for="field in fieldList" v-bind:key="field.id"
                    @dblclick="addNewField(field)">{{ field }}
                </option>
            </select>
        </div>
        <div class="term-editor-query space-children-v">
            <div class="flex-container flex-nowrap flex-stretch-last">
                <span>As:</span>
                <select v-model="fieldType" @change="comparisonType = schema.terms[fieldType][0]">
                    <option v-for="(v, k) in readableFieldTypes" v-bind:key="v.id"
                        :value="k">{{ v }}
                    </option>
                </select>
            </div>
            <div class="comparison-types flex-container flex-center">
                    <span v-for="q in terms" :key="q.id">
                        <input type="radio" :id="q" name="comparisonType" :value="q"
                            v-model="comparisonType"
                            checked>
                        <label :for="q">{{ q }}</label>
                    </span>
            </div>
            <div class="query-values">
                <div v-if="fieldType === 'string'" class="flex-container flex-center">
                    <span class="fields">
                        field
                    </span>
                    <label for="queryValueText">
                        <i :class="['fas', comparisonType === 'equals' ? 'fa-equals' : 'fa-search' ]"></i>
                    </label>
                    <input type="text" v-model="queryValueText" id="queryValueText" size="10">
                </div>
                <div v-if="fieldType === 'number'" class="flex-container flex-center">
                    <input type="number" v-if="comparisonType === 'range'" v-model="queryValueInt2">
                    <input type="checkbox" v-if="comparisonType === 'range'" v-model="queryGTEqual"
                        id="greaterThanEq">
                    <label for="greaterThanEq" v-if="comparisonType === 'range'">
                        <i :class="['fas', 'fa-less-than' + (queryGTEqual ? '-equal' : '')]"></i>
                    </label>
                    <span class="fields">
                        field
                    </span>
                    <input type="checkbox" v-if="comparisonType === 'range'" v-model="queryLTEqual"
                        id="lessThanEq">
                    <label for="lessThanEq" v-if="comparisonType === 'range'">
                        <i :class="['fas', 'fa-less-than' + (queryLTEqual ? '-equal' : '')]"></i>
                    </label>
                    <label for="queryValueInt1" v-if="comparisonType === 'equals'"><i
                        class="fas fa-equals"></i></label>
                    <input type="number" v-model="queryValueInt1" id="queryValueInt1">
                </div>
                <div v-if="fieldType === 'geo'" class="flex-container flex-center">
                    <div class="dataset-map"></div>
                </div>
            </div>
            <div class="query-submit">
                <button @click="submitTerm" class="btn btn-primary">Save</button>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name:     'TermEditor',
        props:    ['schema', 'showEditor', 'resourceIds', 'existingTerm'],
        data:     function () {
            let data = {
                fieldSearch:        null,
                newFields:          [],
                fieldList:          [],
                fieldType:          'string',
                comparisonType:     'equals',
                queryValueText:     null,
                queryValueInt1:     null,
                queryValueInt2:     null,
                queryLTEqual:       false,
                queryGTEqual:       false,
                readableFieldTypes: {
                    string: 'Text',
                    number: 'Number',
                    geo:    'Geo',
                    exists: 'Any'
                }
            };

            let existing = d3.entries(this.existingTerm || {})[0];
            if (existing !== undefined) {
                data.newFields = [...existing.value.fields];
                data.fieldType = existing.key.split('_')[0];
                data.comparisonType = existing.key.split('_')[1];

                if (data.fieldType === 'string') {
                    data.queryValueText = existing.value.value;
                }
                else if (data.fieldType === 'number') {
                    if (data.comparisonType === 'equals') {
                        data.queryValueInt1 = existing.value.value;
                    }
                    else if (data.comparisonType === 'range') {
                        data.queryValueInt1 = existing.value.less_than;
                        data.queryValueInt2 = existing.value.greater_than;
                        data.queryLTEqual = existing.value.less_than_inclusive;
                        data.queryGTEqual = existing.value.greater_than_inclusive;
                    }
                }
            }

            return data;
        },
        mounted:  function () {
            this.getFieldList();
        },
        computed: {
            terms:     function () {
                let schemaTerms = this.schema.terms[this.fieldType];
                let emptyTerms  = schemaTerms.length === 1 && (schemaTerms[0] === '' || schemaTerms[0] === null);
                return emptyTerms ? [] : schemaTerms;
            },
            queryType: function () {
                return this.comparisonType !== '' ? [this.fieldType, this.comparisonType].join('_') : this.fieldType;
            },
            query: function () {
                let queryData = {
                    fields: this.newFields
                };

                if (this.fieldType === 'string') {
                    queryData['value'] = this.queryValueText;
                }
                else if (this.fieldType === 'number') {
                    if (this.comparisonType === 'equals') {
                        queryData['value'] = this.queryValueInt1;
                    }
                    else if (this.comparisonType === 'range') {
                        queryData['less_than'] = this.queryValueInt1;
                        queryData['greater_than'] = this.queryValueInt2;
                        queryData['less_than_inclusive'] = this.queryLTEqual;
                        queryData['greater_than_inclusive'] = this.queryGTEqual;
                    }
                }

                let q = {};
                q[this.queryType] = queryData;
                return q;
            }
        },
        methods:  {
            addNewField:  function (field) {
                this.newFields.push(field);
            },
            deleteField:  function (index) {
                this.$delete(this.newFields, index);
            },
            closeDialog:  function () {
                this.$parent.showEditor = false;
            },
            getFieldList: function () {
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
                                                    resource_ids: this.resourceIds,
                                                    prefix:       this.fieldSearch,
                                                    lowercase:    true
                                                }),
                }).then(response => {
                    return response.json();
                }).then(data => {
                    this.fieldList = Object.keys(data.result.fields).sort();
                });
            },
            submitTerm: function () {
                if (this.existingTerm !== undefined) {
                    this.$parent.filterItem = this.query;
                }
                else {
                    this.$parent.siblings.push(this.query);
                }
                this.closeDialog();
            }
        },
        watch:    {
            fieldSearch: function () {
                this.getFieldList();
            }
        }
    }
</script>
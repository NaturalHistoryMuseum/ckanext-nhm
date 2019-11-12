<template>
    <div class="term-editor floating flex-container flex-nowrap flex-stretch-height">
        <i class="fas fa-caret-square-left" @click="closeDialog"></i>
        <div class="term-editor-fields space-children-v" v-if="fieldType !== 'geo'">
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
                    <input type="text" v-model="values.string.value" id="queryValueText" size="10">
                </div>
                <div v-if="fieldType === 'number'" class="flex-container flex-center">
                    <input type="number" v-if="comparisonType === 'range'"
                        v-model="values.number.greater_than">
                    <input type="checkbox" v-if="comparisonType === 'range'"
                        v-model="values.number.greater_than_inclusive"
                        id="greaterThanEq">
                    <label for="greaterThanEq" v-if="comparisonType === 'range'">
                        <i :class="['fas', 'fa-less-than' + (values.number.greater_than_inclusive ? '-equal' : '')]"></i>
                    </label>
                    <span class="fields">
                        field
                    </span>
                    <input type="checkbox" v-if="comparisonType === 'range'"
                        v-model="values.number.less_than_inclusive"
                        id="lessThanEq">
                    <label for="lessThanEq" v-if="comparisonType === 'range'">
                        <i :class="['fas', 'fa-less-than' + (values.number.less_than_inclusive ? '-equal' : '')]"></i>
                    </label>
                    <label for="queryValueInt1" v-if="comparisonType === 'equals'"><i
                        class="fas fa-equals"></i></label>
                    <input type="number" v-if="comparisonType === 'range'"
                        v-model="values.number.less_than">
                    <input type="number" v-if="comparisonType === 'equals'"
                        v-model="values.number.value" id="queryValueInt1">
                </div>
                <div v-if="fieldType === 'geo'" class="flex-container flex-column flex-center">
                    <div class="flex-container flex-center" v-if="comparisonType === 'point'">
                        <label for="queryValueLat">Lat</label>
                        <input type="text" v-model="values.geo.latitude" id="queryValueLat"
                            size="5">
                        <label for="queryValueLon">Lon</label>
                        <input type="text" v-model="values.geo.longitude" id="queryValueLon"
                            size="5">
                        <label for="queryValueInt1"></label>
                        <input type="number" v-model="values.geo.radius">
                        <select v-model="values.geo.radius_unit">
                            <option v-for="unit in geoEnums.radiusUnits" :key="unit.id">{{ unit }}
                            </option>
                        </select>
                    </div>
                    <div class="flex-container flex-center" v-if="comparisonType === 'named_area'">
                        <label for="geoCategory">Category</label>
                        <select v-model="geoCategory" id="geoCategory">
                            <option v-for="(options, cat) in geoEnums.named" :key="cat.id">{{ cat }}</option>
                        </select>
                        <select v-model="values.geo[geoCategory]">
                            <option v-for="area in (geoEnums.named[geoCategory] || [])" :key="area.id">{{ area }}
                            </option>
                        </select>
                    </div>
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
                geoEnums:           {
                    radiusUnits: this.schema.raw.definitions.term.properties.geo_point.properties.radius_unit.enum,
                    named:       d3.nest()
                                   .key((d) => d.key)
                                   .rollup((d) => {
                                       return d[0].value.enum;
                                   })
                                   .object(d3.entries(this.schema.raw.definitions.term.properties.geo_named_area.properties))
                },
                geoCategory: null,
                fieldType:          'string',
                comparisonType:     'equals',
                values:             {
                    string: {
                        value: null
                    },
                    number: {
                        greater_than:           null,
                        less_than:              null,
                        greater_than_inclusive: null,
                        less_than_inclusive:    null,
                        value:                  null
                    },
                    geo:    {
                        latitude:    null,
                        longitude:   null,
                        radius:      0,
                        radius_unit: null,
                        country: null,
                        geography: null,
                        marine: null
                    },
                },
                readableFieldTypes: {
                    string: 'Text',
                    number: 'Number',
                    geo:    'Geo',
                    exists: 'Any'
                }
            };

            let existing = d3.entries(this.existingTerm || {})[0];
            if (existing !== undefined) {
                data.newFields      = [...(existing.value.fields || [])];
                data.fieldType      = existing.key.split('_')[0];
                data.comparisonType = existing.key.slice(existing.key.indexOf('_') + 1);

                if (d3.keys(data.values).includes(data.fieldType)) {
                    let updatedValues = {};

                    d3.keys(data.values[data.fieldType]).forEach((k) => {
                        updatedValues[k] = existing.value[k] || null;
                    });

                    if (existing.key === 'geo_named_area') {
                        data.geoCategory = d3.keys(existing.value).filter((k) => {
                            return d3.keys(data.geoEnums.named).includes(k);
                        })[0];
                    }

                    data.values[data.fieldType] = updatedValues;
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
            query:     function () {
                let queryData = {};

                if (this.fieldType !== 'geo') {
                    queryData.fields = this.newFields;
                }

                if (d3.keys(this.values).includes(this.fieldType)) {
                    d3.entries(this.values[this.fieldType]).forEach((e) => {
                        if (e.value !== null) {
                            queryData[e.key] = e.value;
                        }
                    });
                }

                let q             = {};
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
            submitTerm:   function () {
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
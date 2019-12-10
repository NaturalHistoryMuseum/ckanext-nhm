<template>
    <div class="term-editor floating flex-container flex-smallwrap flex-stretch-height">
        <i class="fas fa-caret-square-left" @click="closeDialog"></i>
        <div class="term-editor-fields space-children-v" v-if="fieldType !== 'geo'">
            <div class="flex-container flex-wrap flex-wrap-spacing">
                            <span class="fields"
                                  v-for="(field, index) in newFields"
                                  v-bind:key="field.id">
                                {{ field }}
                                <i class="delete-field fas fa-times-circle fa-xs"
                                   @click="deleteField(index)"></i>
                            </span>
            </div>
            <FieldPicker :callback="addNewField"
                         :resource-ids="resourceIds"></FieldPicker>
        </div>
        <div class="term-editor-query space-children-v">
            <div class="flex-container flex-nowrap flex-stretch-last">
                <span>As:</span> <select v-model="fieldType"
                                         @change="comparisonType = schema.terms[fieldType][0]">
                <option v-for="(v, k) in readableFieldTypes" v-bind:key="v.id" :value="k">{{ v }}
                </option>
            </select>
            </div>
            <div class="comparison-types flex-container flex-center">
                    <span v-for="q in terms" :key="q.id">
                        <input type="radio"
                               :id="q"
                               name="comparisonType"
                               :value="q"
                               v-model="comparisonType"
                               checked>
                        <label :for="q">{{ q }}</label>
                    </span>
            </div>
            <div class="query-values">
                <keep-alive>
                    <component :is="fieldType"
                               :comparison-type="comparisonType"
                               :existing-term-id="existingTermId"
                               v-on:set-query-values="setQueryValues"></component>
                </keep-alive>
            </div>
            <div class="query-submit">
                <button @click="submitTerm" class="btn btn-primary">Save</button>
            </div>
        </div>
    </div>
</template>

<script>
    import * as d3 from 'd3-collection';
    import {mapMutations, mapState} from 'vuex'
    import TextEditor from './editors/TextEditor.vue';
    import NumberEditor from './editors/NumberEditor.vue';
    import GeoEditor from './editors/GeoEditor.vue';
    import OtherEditor from './editors/OtherEditor.vue';
    import FieldPicker from './misc/FieldPicker.vue';

    export default {
        name:       'TermEditor',
        components: {
            FieldPicker: FieldPicker,
            string:      TextEditor,
            number:      NumberEditor,
            geo:         GeoEditor,
            other:       OtherEditor,
        },
        props:      ['existingTermId', 'parentId'],
        data:       function () {
            let data = {
                newFields:          [],
                fieldType:          'string',
                comparisonType:     'equals',
                queryValues:        {},
                readableFieldTypes: {
                    string: 'Text',
                    number: 'Number',
                    geo:    'Geo',
                    other:  'Any'
                }
            };

            if (this.existingTermId !== undefined) {
                let existing        = this.$store.getters['filters/getFilterById'](this.existingTermId);
                data.newFields      = [...(existing.content.fields || [])];
                data.fieldType      = existing.key.includes('_') ? existing.key.split('_')[0] : 'other';
                data.comparisonType = existing.key.slice(existing.key.indexOf('_') + 1);
            }

            return data;
        },
        computed:   {
            ...mapState('constants', ['schema']),
            ...mapState(['resourceIds']),
            terms:     function () {
                let schemaTerms = this.schema.terms[this.fieldType];
                let emptyTerms  = schemaTerms.length === 1 && (schemaTerms[0] === '' || schemaTerms[0] === null);
                return emptyTerms ? [] : schemaTerms;
            },
            queryType: function () {
                return this.fieldType !== 'other' ? [this.fieldType, this.comparisonType].join('_') : this.comparisonType;
            },
            query:     function () {
                let queryData = {};

                if (this.fieldType !== 'geo') {
                    queryData.fields = this.newFields;
                }

                if (Array.isArray(this.queryValues)) {
                    // this is pretty much only for geo_custom_area
                    queryData = this.queryValues;
                }
                else {
                    d3.entries(this.queryValues).forEach((e) => {
                        if (e.value !== null) {
                            queryData[e.key] = e.value;
                        }
                    });
                }

                return queryData;
            }
        },
        methods:    {
            ...mapMutations('filters', ['changeKey', 'changeContent', 'addTerm']),
            setQueryValues: function (queryValues) {
                this.queryValues = queryValues;
            },
            addNewField:    function (field) {
                this.newFields.push(field);
            },
            deleteField:    function (index) {
                this.$delete(this.newFields, index);
            },
            closeDialog:    function () {
                this.$parent.showEditor = false;
            },
            submitTerm:     function () {
                if (this.existingTermId !== undefined) {
                    this.changeKey({key: this.queryType, id: this.existingTermId});
                    this.changeContent({content: this.query, id: this.existingTermId});
                }
                else {
                    this.addTerm({
                                     parentId: this.parentId,
                                     key:      this.queryType,
                                     content:  this.query
                                 })
                }
                this.closeDialog();
            },
            resetQuery: function () {
                this.queryValues = {};
            }
        },
        watch: {
            fieldType() {
                this.resetQuery();
            },
            comparisonType() {
                this.resetQuery();
            }
        }
    }
</script>
<template>
  <div class="term-editor floating flex-container flex-stretch-height">
    <i class="fas fa-caret-square-left" @click="closeDialog" role="button"></i>
    <div
      class="term-editor-fields term-editor-block space-children-v"
      v-if="fieldType !== 'geo'"
    >
      <div class="flex-container flex-wrap flex-wrap-spacing field-list">
        <span
          class="fields"
          v-for="(field, index) in newFields"
          v-bind:key="field.id"
        >
          {{ field }}
          <i
            class="delete-field fas fa-times-circle fa-xs"
            @click="deleteField(index)"
          ></i>
        </span>
      </div>
      <FieldPicker
        :callback="addNewField"
        :resource-ids="resourceIds"
        :selected-fields="newFields"
      ></FieldPicker>
    </div>
    <div class="term-editor-query term-editor-block space-children-v">
      <div class="flex-container flex-nowrap flex-stretch-last">
        <span>As:</span>
        <select
          v-model="fieldType"
          title="Select what type to treat the field's contents as"
          @change="comparisonType = schema.terms[fieldType][0]"
        >
          <option
            v-for="(v, k) in readableFieldTypes"
            v-bind:key="v.id"
            :value="k"
          >
            {{ v }}
          </option>
        </select>
      </div>
      <div class="comparison-types flex-container flex-center">
        <span v-for="q in terms" :key="q.id">
          <input
            type="radio"
            :id="q"
            name="comparisonType"
            :value="q"
            v-model="comparisonType"
            checked
          />
          <label :for="q">{{ q }}</label>
        </span>
      </div>
      <div class="query-values">
        <keep-alive>
          <component
            :is="fieldType"
            :comparison-type="comparisonType"
            :existing-term-id="existingTermId"
            v-on:set-query-values="setQueryValues"
            v-on:pressed-enter="submitTerm"
          ></component>
        </keep-alive>
      </div>
      <div class="flex-container flex-column flex-stretch-height">
        <label for="termNameInput" class="sr-only">Name (optional)</label>
        <input
          id="termNameInput"
          type="text"
          v-model="termName"
          @keyup.enter="submitTerm"
          placeholder="name (optional)"
        />
      </div>
      <div class="query-submit">
        <button @click="submitTerm" class="btn btn-primary no-icon">
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3-collection';
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
import TextEditor from './editors/TextEditor.vue';
import NumberEditor from './editors/NumberEditor.vue';
import GeoEditor from './editors/GeoEditor.vue';
import OtherEditor from './editors/OtherEditor.vue';
import FieldPicker from './misc/FieldPicker.vue';

export default {
  name: 'TermEditor',
  components: {
    FieldPicker: FieldPicker,
    string: TextEditor,
    number: NumberEditor,
    geo: GeoEditor,
    other: OtherEditor,
  },
  props: ['existingTermId', 'parentId'],
  data: function () {
    let data = {
      newFields: [],
      fieldType: 'string',
      comparisonType: 'equals',
      termName: null,
      queryValues: {},
      readableFieldTypes: {
        string: 'Text',
        number: 'Number',
        geo: 'Geo',
        other: 'Any',
      },
    };

    if (this.existingTermId !== undefined) {
      let existing = this.$store.getters['results/query/filters/getFilterById'](
        this.existingTermId,
      );
      data.newFields = [...(existing.content.fields || [])];
      data.fieldType = existing.key.includes('_')
        ? existing.key.split('_')[0]
        : 'other';
      data.comparisonType = existing.key.slice(existing.key.indexOf('_') + 1);
      data.termName = existing.display.name;
    }

    return data;
  },
  computed: {
    ...mapState(['schema']),
    ...mapState('results/query/resources', ['resourceIds']),
    ...mapGetters('results/query/filters', ['getFilterById']),
    terms: function () {
      let schemaTerms = this.schema.terms[this.fieldType];
      let emptyTerms =
        schemaTerms.length === 1 &&
        (schemaTerms[0] === '' || schemaTerms[0] === null);
      return emptyTerms ? [] : schemaTerms;
    },
    queryType: function () {
      return this.fieldType !== 'other'
        ? [this.fieldType, this.comparisonType].join('_')
        : this.comparisonType;
    },
    query: function () {
      let queryData = {};

      if (this.fieldType !== 'geo') {
        queryData.fields = this.newFields;
      }

      if (Array.isArray(this.queryValues)) {
        // this is pretty much only for geo_custom_area
        queryData = this.queryValues;
      } else {
        d3.entries(this.queryValues).forEach((e) => {
          if (e.value !== null) {
            queryData[e.key] = e.value;
          }
        });
      }

      return queryData;
    },
  },
  methods: {
    ...mapMutations('results/query/filters', [
      'changeKey',
      'changeContent',
      'changeName',
    ]),
    ...mapActions('results/query/filters', ['addTerm']),
    setQueryValues: function (queryValues) {
      this.queryValues = queryValues;
    },
    addNewField: function (field) {
      this.newFields.push(field);
    },
    deleteField: function (index) {
      this.$delete(this.newFields, index);
    },
    closeDialog: function () {
      this.$parent.showEditor = false;
    },
    submitTerm: function () {
      if (this.existingTermId !== undefined) {
        this.changeKey({ key: this.queryType, id: this.existingTermId });
        this.changeContent({ content: this.query, id: this.existingTermId });
        this.changeName({ name: this.termName, id: this.existingTermId });
      } else {
        this.addTerm({
          parent: this.parentId,
          key: this.queryType,
          content: this.query,
          display: {
            name: this.termName,
          },
        });
      }
      this.closeDialog();
    },
    resetQuery: function () {
      this.queryValues = {};
    },
  },
  watch: {
    fieldType() {
      this.resetQuery();
    },
    comparisonType() {
      this.resetQuery();
    },
  },
};
</script>

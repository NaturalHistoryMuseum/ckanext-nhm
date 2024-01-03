<template>
  <div class="space-children-v field-picker" :class="classes">
    <div
      class="flex-container flex-nowrap flex-stretch-first flex-stretch-height"
    >
      <input
        type="text"
        class="full-width"
        name="fieldSearch"
        id="fieldSearch"
        title="Search for a field by prefix"
        value=""
        autocomplete="off"
        placeholder="field name"
        v-model="fieldSearch"
      />
      <button class="btn btn-mini" @click="addCurrentField">
        <i class="fas fa-arrow-circle-up" style="margin: 0 !important"></i>
      </button>
    </div>
    <select
      class="full-width"
      size="10"
      title="Select a field"
      v-model="currentField"
      @keyup.enter="addCurrentField"
    >
      <option
        v-for="field in selectableFields"
        v-bind:key="field.id"
        @click="callback(field)"
        class="term-editor-option"
      >
        {{ field }}
      </option>
    </select>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { post } from '../../store/utils';

export default {
  name: 'FieldPicker',
  data: function () {
    return {
      fieldSearch: null,
      fieldList: [],
      currentField: null,
    };
  },
  props: ['callback', 'resourceIds', 'classes', 'selectedFields'],
  computed: {
    ...mapState('results', ['resultData']),
    selectableFields() {
      const existingFields = this.selectedFields || []; // just in case it's null
      return this.fieldList.filter((f) => !existingFields.includes(f));
    },
  },
  methods: {
    getFieldList() {
      const vue = this;
      post('datastore_field_autocomplete', {
        resource_ids: vue.resourceIds,
        text: (vue.fieldSearch || '').toLowerCase(),
        lowercase: true,
      })
        .then((data) => {
          if (data.success) {
            vue.fieldList = Object.keys(data.result.fields).sort();
          } else {
            throw Error;
          }
        })
        .catch((error) => {
          vue.fieldList = [];
        });
    },
    addCurrentField() {
      this.callback(this.currentField);
    },
  },
  mounted: function () {
    this.getFieldList();
  },
  watch: {
    fieldSearch() {
      this.getFieldList();
    },
    resultData: {
      handler() {
        this.getFieldList();
      },
      deep: true,
    },
  },
};
</script>

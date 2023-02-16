<template>
  <div class="space-children-v field-picker" :class="classes">
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
    <select class="full-width" size="10" title="Select a field">
      <option
        v-for="field in fieldList"
        v-bind:key="field.id"
        @click="callback(field)"
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
    };
  },
  props: ['callback', 'resourceIds', 'classes'],
  computed: {
    ...mapState('results', ['resultData']),
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

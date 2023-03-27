<template>
  <pre>
        {{ resultData.result }}
    </pre
  >
</template>

<script>
import { mapGetters, mapMutations, mapState, mapActions } from 'vuex';
import axios from 'axios';
import SparkMD5 from 'spark-md5';
import debounce from 'lodash.debounce';

export default {
  name: 'BaseView',
  data: function () {
    return {
      showFields: false,
    };
  },
  computed: {
    ...mapState('results', ['resultData', 'page']),
    ...mapState('results/display', ['headers']),
    ...mapState('results/images', ['imageRecords']),
    ...mapGetters('results', ['total', 'records']),
    ...mapGetters('results/display', ['licenceFromId']),
    ...mapGetters('results/images', ['loadedImageRecords']),
    ...mapGetters('results/query/resources', ['resourceDetails']),
  },
  methods: {
    ...mapMutations('results/display', [
      'removeHeader',
      'moveHeader',
      'setViewerImage',
      'addPageImages',
    ]),
    ...mapActions('results/images', ['loadAndCheckImages']),
    getValue(item, field) {
      let v = { ...item };
      let subFields = field.split('.');

      let subItems = (parentItem, subField) => {
        if (Array.isArray(parentItem)) {
          return parentItem.map((x) => subItems(x, subField)).join('; ');
        } else {
          return parentItem[subField];
        }
      };

      for (let i = 0; i < subFields.length; i++) {
        try {
          v = subItems(v, subFields[i]);
        } catch (e) {
          break;
        }
      }
      return v;
    },
  },
};
</script>

import Vue from 'vue';
import * as d3 from 'd3-collection';
import { get, post } from '../utils';

let display = {
  namespaced: true,
  state: {
    view: 'Table',
    headers: [],
    licences: {},
    viewerImageIndex: 0,
    viewerImagePage: [],
    showImage: false,
    recordTag: 'result',
    filteredRecordTag: 'result$', // replace $ with s to make plural
  },
  getters: {
    viewerImage: (state) => {
      return state.viewerImagePage[state.viewerImageIndex];
    },
    recordHeader: (state) => (recordCount) => {
      return `${recordCount.toLocaleString('en-GB')} ${state.recordTag}${
        recordCount === 1 ? '' : 's'
      }`;
    },
    filteredRecordHeader: (state) => (recordCount) => {
      return `${recordCount.toLocaleString(
        'en-GB',
      )} ${state.filteredRecordTag.replace('$', recordCount === 1 ? '' : 's')}`;
    },
    licenceFromId: (state) => (licenceId) => {
      const noLicence = {
        status: 'active',
        maintainer: '',
        od_conformance: 'not reviewed',
        family: '',
        osd_conformance: 'not reviewed',
        domain_data: 'False',
        title: 'Licence not specified',
        url: 'https://opensource.org/licenses',
        is_generic: 'True',
        is_okd_compliant: false,
        is_osi_compliant: false,
        domain_content: 'False',
        domain_software: 'False',
        id: 'notspecified',
      };

      if (state.licences.length === 0) {
        return noLicence;
      }

      return state.licences[licenceId] || noLicence;
    },
  },
  mutations: {
    setView(state, viewName) {
      state.view = viewName;
    },
    setViewerImage(state, imageIndex) {
      state.viewerImageIndex = imageIndex;
      state.showImage = true;
    },
    addPageImages(state, images) {
      state.viewerImagePage = images;
    },
    appendPageImage(state, image) {
      state.viewerImagePage.push(image);
    },
    hideImage(state) {
      state.showImage = false;
      state.viewerImage = 0;
    },
    addCustomHeader(state, field) {
      state.headers.push([field]);
    },
    removeHeader(state, headerIndex) {
      Vue.delete(state.headers, headerIndex);
    },
    moveHeader(state, payload) {
      let header = state.headers[payload.ix];
      let target = state.headers[payload.ix + payload.by];
      Vue.set(state.headers, payload.ix + payload.by, header);
      Vue.set(state.headers, payload.ix, target);
    },
    setFilteredRecordTag(state, template) {
      state.filteredRecordTag = template;
    },
    resetFilteredRecordTag(state) {
      state.filteredRecordTag = state.recordTag + '$';
    },
  },
  actions: {
    getHeaders(context, payload) {
      context.state.headers = [];
      let headers = [];

      d3.values(payload.filters).forEach((f) => {
        if (
          f.content.fields !== undefined &&
          !['string_equals', 'number_equals'].includes(f.key)
        ) {
          headers.push(f.content.fields);
        }
      });

      payload.request['size'] = 15;

      post('datastore_guess_fields', payload.request)
        .then((data) => {
          if (data.success) {
            headers = headers.concat(data.result.map((f) => d3.keys(f.fields)));
          }
        })
        .catch((e) => {
          console.log(e);
        })
        .finally(() => {
          headers.forEach((h) => {
            if (
              !context.state.headers
                .map((x) => JSON.stringify(x))
                .includes(JSON.stringify(h))
            ) {
              context.state.headers.push(h);
            }
          });
        });
    },
    getLicences(context) {
      get('license_list').then((data) => {
        if (data.success) {
          context.state.licences = d3
            .nest()
            .key((l) => l.id)
            .rollup((l) => {
              let licence = l[0];
              licence.url =
                licence.url === ''
                  ? 'https://opensource.org/licenses'
                  : licence.url;
              return licence;
            })
            .object(data.result);
        }
      });
    },
  },
};

export default display;

import * as d3 from 'd3-collection';

let dynamicPresets = {
  namespaced: true,
  state: {
    hasImage: {
      name: 'Has Image',
      args: {
        state: [],
        getters: ['results/query/resources/currentResourceDetails'],
      },
    },
  },
  getters: {
    presets: (state) => {
      return d3
        .nest()
        .key((p) => p.key)
        .rollup((p) => p[0].value.name)
        .object(d3.entries(state));
    },
    keys: (state) => {
      return d3.entries(state).map((p) => p.key);
    },
    hasImage: (state) => (args) => {
      let imageFields = [];

      args['results/query/resources/currentResourceDetails']
        .map((r) => {
          return r.raw._image_field;
        })
        .filter((f) => {
          return f !== null && f !== undefined && f !== 'None';
        })
        .forEach((f) => {
          if (!imageFields.includes(f)) {
            imageFields.push(f);
          }
        });

      let preset = {
        key: 'exists',
        content: {
          fields: imageFields,
        },
        type: 'term',
        display: {
          name: state.hasImage.name,
        },
      };

      if (imageFields.length === 0) {
        preset.content.error =
          'The selected datasets do not have image fields.';
      }

      return [preset];
    },
  },
};

export default dynamicPresets;

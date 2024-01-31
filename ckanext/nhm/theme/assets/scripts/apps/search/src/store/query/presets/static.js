import * as d3 from 'd3-collection';

let staticPresets = {
  namespaced: true,
  state: {
    birdwingButterflies: {
      name: 'Birdwing Butterfly Digitisation',
      content: [
        {
          type: 'term',
          key: 'string_equals',
          content: {
            fields: ['project'],
            value: 'Birdwing Butterfly Digitisation',
          },
        },
      ],
    },
    noGbifIssues: {
      name: 'No GBIF Issues',
      content: [
        {
          type: 'group',
          key: 'not',
          content: [],
        },
        {
          type: 'term',
          key: 'exists',
          content: {
            fields: ['gbifIssue'],
          },
        },
      ],
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
  },
};

export default staticPresets;

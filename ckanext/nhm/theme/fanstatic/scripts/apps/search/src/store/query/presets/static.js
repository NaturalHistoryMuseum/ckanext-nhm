import * as d3 from 'd3-collection';

let staticPresets = {
    namespaced: true,
    state:      {
        specimensHasImage: {
            name:    'Has Image (Specimens Collection)',
            type: 'term',
            key:     'exists',
            content: {
                fields: [
                    'associatedMedia'
                ]
            }
        }
    },
    getters:    {
        presets: (state) => {
            return d3.nest()
                     .key(p => p.key)
                     .rollup(p => p[0].value.name)
                     .object(d3.entries(state));
        },
        keys: (state) => {
            return d3.entries(state).map(p => p.key);
        }
    }
};

export default staticPresets;
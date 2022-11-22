import * as d3 from 'd3-collection';

let staticPresets = {
    namespaced: true,
    state:      {
        specimensHasImage: {
            type: 'term',
            key:     'string_equals',
            content: {
                fields: [
                    'project'
                ],
                value: 'Birdwing Butterfly Digitisation'
            },
            display: {
                name: 'Birdwing Butterfly Digitisation'
            }
        }
    },
    getters:    {
        presets: (state) => {
            return d3.nest()
                     .key(p => p.key)
                     .rollup(p => p[0].value.display.name)
                     .object(d3.entries(state));
        },
        keys: (state) => {
            return d3.entries(state).map(p => p.key);
        }
    }
};

export default staticPresets;

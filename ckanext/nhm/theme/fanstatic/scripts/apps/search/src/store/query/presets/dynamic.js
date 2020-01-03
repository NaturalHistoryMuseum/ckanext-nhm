import * as d3 from 'd3-collection';

let dynamicPresets = {
    namespaced: true,
    state:      {
        hasImage: {
            name: 'Has Image',
            args: {
                state:   [],
                getters: [
                    'results/query/resources/currentResourceDetails'
                ]
            }
        }
    },
    getters:    {
        presets:  (state) => {
            return d3.nest()
                     .key(p => p.key)
                     .rollup(p => p[0].value.name)
                     .object(d3.entries(state));
        },
        keys:     (state) => {
            return d3.entries(state).map(p => p.key);
        },
        hasImage: (state) => (args) => {
            let imageFields = [];

            args['results/query/resources/currentResourceDetails'].map(r => {
                return r.raw._image_field
            }).filter(f => {
                return f !== null && f !== undefined && f !== 'None';
            }).forEach(f => {
                if (!imageFields.includes(f)) {
                    imageFields.push(f)
                }
            });

            return {
                key:     'exists',
                content: {
                    fields: imageFields
                },
                name:    state.hasImage.name,
                type:    'term'
            };
        }
    }
};

export default dynamicPresets;
ckan.module('multisearch', function () {
    let self = null;
    return {
        initialize: function () {

            Vue.component('schema-loader', function (resolve, reject) {
                search.refParser.dereference('/querySchemas/v1.0.0/v1.0.0.json')
                    .then(data => {
                        let groups = Object.keys(data.definitions.group.properties);
                        let terms  = d3.nest()
                                       .key(t => {
                                           return t.key.split('_')[0];
                                       })
                                       .rollup(leaves => {
                                           return leaves.map((l) => l.key.slice(l.key.indexOf('_') + 1) || '')
                                       })
                                       .object(d3.entries(data.definitions.term.properties));
                        console.log(data);
                        return {
                            groups: groups,
                            terms:  terms,
                            raw: data
                        };
                    })
                    .then(schema => {
                        resolve({
                                    data:       function () {
                                        return {
                                            schema: schema
                                        }
                                    },
                                    components: {search},
                                    template:   '<search v-bind:schema="schema"></search>'
                                })
                    });
            });

            new Vue({
                        delimiters: ['[[', ']]'],
                    }).$mount('#searchApp');
        },
    };
});

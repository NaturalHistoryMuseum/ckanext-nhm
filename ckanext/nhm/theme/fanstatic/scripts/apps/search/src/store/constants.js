import $RefParser from 'json-schema-ref-parser';
import * as d3 from 'd3-collection';

let constants = {
    namespaced: true,
    state:      {
        loading:           true,
        loadError:         false,
        schema:            {
            groups: [],
            terms:  {},
            raw:    {}
        },
        packageList:       [],
        readableGroupType: {
            'and': 'ALL OF',
            'or':  'ANY OF',
            'not': 'NONE OF'
        }
    },
    getters:    {
        getGroup: state => groupId => {
            return state.readableGroupType[groupId];
        },
        resourceDetails: state => {
            let lookup = {};

            state.packageList.forEach(p => {
                p.resources.forEach(r => {
                    lookup[r.id] = r;
                })
            });

            return lookup;
        }
    },
    actions:    {
        getSchema(context) {
            context.state.loading   = true;
            context.state.loadError = false;
            $RefParser.dereference('/querySchemas/v1.0.0/v1.0.0.json', {resolve: {http: {timeout: 2000}}})
                      .then(data => {
                          let groups = d3.keys(data.definitions.group.properties);
                          let terms  = d3.nest()
                                         .key(t => t.key.includes('_') ? t.key.split('_')[0] : 'other')
                                         .rollup(leaves => leaves.map((l) => l.key.slice(l.key.indexOf('_') + 1) || ''))
                                         .object(d3.entries(data.definitions.term.properties));
                          return {
                              groups: groups,
                              terms:  terms,
                              raw:    data
                          };
                      })
                      .then(schema => {
                          context.state.schema  = schema;
                          context.state.loading = false;
                      }, error => {
                          context.state.loading   = false;
                          context.state.loadError = true;
                      });
        },
        getPackageList(context) {
            fetch('/api/3/action/current_package_list_with_resources', {
                method: 'GET'
            }).then(response => {
                return response.json();
            }).then(data => {
                context.state.resourceToPackage = {};
                context.state.packageList       = data.result.map(pkg => {
                    let resources = pkg.resources.filter(r => {
                        return r.datastore_active;
                    }).map(r => {
                        return {
                            name: r.name,
                            id:   r.id,
                            package_id: r.package_id,
                            package_name: pkg.title
                        }
                    });
                    return {
                        name:        pkg.title,
                        id:          pkg.id,
                        resources:   resources,
                        resourceIds: resources.map(r => r.id)
                    }
                }).filter(pkg => pkg.resources.length > 0);
            });
        }
    },
};

export default constants;
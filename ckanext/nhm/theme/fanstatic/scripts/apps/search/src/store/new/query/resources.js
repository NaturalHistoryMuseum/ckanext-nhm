import {get} from '../utils'

let resources = {
    namespaced: false,
    state:      {
        resourceIds: [],
        packageList: [],
    },
    getters:    {
        resourceDetails: state => {
            let lookup = {};

            state.packageList.forEach(p => {
                p.resources.forEach(r => {
                    lookup[r.id] = r;
                })
            });

            return lookup;
        },
        sortedResources: (state) => {
            return state.resourceIds.sort();
        },
        allResourceIds: (state) => {
            let resourceIds = [];
            state.packageList.forEach((pkg) => {
                resourceIds = resourceIds.concat(pkg.resourceIds)
            });
            return resourceIds;
        },
        invalidResourceIds: (state, getters) => (resourceIds) => {
            let invalidIds = resourceIds.filter(r => {
                !getters.allResourceIds.includes(r);
            });
            return invalidIds.length > 0 ? invalidIds : null;
        }
    },
    mutations:  {
        setResourceIds(state, resourceIds) {
            state.resourceIds = resourceIds;
        },
        selectAllResources(state) {
            let resourceIds = [];
            state.packageList.forEach((pkg) => {
                resourceIds = resourceIds.concat(pkg.resourceIds)
            });
            state.resourceIds = resourceIds;
        },
        togglePackageResources(state, packageIx) {
            let pkg           = state.packageList[packageIx];
            let isInResources = pkg.resourceIds.some((r) => {
                return state.resourceIds.includes(r);
            });
            if (isInResources) {
                state.resourceIds = state.resourceIds.filter((resourceId) => {
                    return !pkg.resourceIds.includes(resourceId);
                });
            }
            else {
                state.resourceIds = state.resourceIds.concat(pkg.resourceIds.filter((x) => {
                    return !state.resourceIds.includes(x);
                }));
            }
        },
    },
    actions:    {
        getPackageList(context) {
            get('current_package_list_with_resources?limit=10000')
                .then(data => {
                    context.state.packageList = data.result.map(pkg => {
                        let resources = pkg.resources.filter(r => {
                            return r.datastore_active;
                        }).map(r => {
                            return {
                                name:         r.name,
                                id:           r.id,
                                package_id:   r.package_id,
                                package_name: pkg.title,
                                raw:          r
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
    }
};

export default resources;
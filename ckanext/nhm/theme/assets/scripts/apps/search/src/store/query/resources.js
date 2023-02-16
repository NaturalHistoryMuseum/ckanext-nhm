import { get } from '../utils';
import * as d3 from 'd3-collection';
import Vue from 'vue';

let resources = {
  namespaced: true,
  state: {
    resourceIds: [],
    packageList: [],
  },
  getters: {
    resourceDetails: (state) => {
      let lookup = {};

      state.packageList.forEach((p) => {
        p.resources.forEach((r) => {
          lookup[r.id] = r;
        });
      });

      return lookup;
    },
    currentResourceDetails: (state, getters) => {
      let resourceDetails = d3.entries(getters.resourceDetails);
      if (state.resourceIds.length > 0) {
        resourceDetails = resourceDetails.filter((r) => {
          return state.resourceIds.includes(r.key);
        });
      }
      return resourceDetails.map((r) => r.value);
    },
    sortedResources: (state) => {
      return state.resourceIds.sort();
    },
    allResourceIds: (state) => {
      let resourceIds = [];
      state.packageList.forEach((pkg) => {
        resourceIds = resourceIds.concat(pkg.resourceIds);
      });
      return resourceIds;
    },
    invalidResourceIds: (state, getters) => (resourceIds) => {
      let invalidIds = resourceIds.filter((r) => {
        return !getters.allResourceIds.includes(r);
      });
      return invalidIds.length > 0 ? invalidIds : null;
    },
    packageResources: (state) => (packageIx) => {
      let pkg = state.packageList[packageIx];
      return pkg.resourceIds;
    },
  },
  mutations: {
    setResourceIds(state, resourceIds) {
      state.resourceIds = resourceIds;
    },
    selectAllResources(state) {
      let resourceIds = [];
      state.packageList.forEach((pkg) => {
        resourceIds = resourceIds.concat(pkg.resourceIds);
      });
      state.resourceIds = resourceIds;
    },
    togglePackageResources(state, packageIx) {
      let pkg = state.packageList[packageIx];
      let isInResources = pkg.resourceIds.some((r) => {
        return state.resourceIds.includes(r);
      });
      if (isInResources) {
        state.resourceIds = state.resourceIds.filter((resourceId) => {
          return !pkg.resourceIds.includes(resourceId);
        });
      } else {
        state.resourceIds = state.resourceIds.concat(
          pkg.resourceIds.filter((x) => {
            return !state.resourceIds.includes(x);
          }),
        );
      }
    },
  },
  actions: {
    getPackageList(context) {
      Vue.set(context.rootState.appState.status.resources, 'loading', true);
      Vue.set(context.rootState.appState.status.resources, 'failed', false);
      return new Promise((resolve, reject) => {
        get('current_package_list_with_resources?limit=10000')
          .then((data) => {
            context.state.packageList = data.result
              .map((pkg) => {
                let resources = pkg.resources
                  .filter((r) => {
                    return r.datastore_active;
                  })
                  .map((r) => {
                    let packageUrl = `/dataset/${pkg.id}`;
                    let resourceUrl = packageUrl + `/resource/${r.id}`;
                    return {
                      raw: r,
                      name: r.name,
                      id: r.id,
                      package_id: r.package_id,
                      package_name: pkg.title,
                      titleField: r._title_field || '_id',
                      imageField: r._image_field,
                      imageDelimiter: r._image_delimiter || '',
                      imageLicence: context.rootGetters[
                        'results/display/licenceFromId'
                      ](r._image_licence),
                      packageUrl,
                      resourceUrl,
                    };
                  });
                return {
                  name: pkg.title,
                  id: pkg.id,
                  resources: resources,
                  resourceIds: resources.map((r) => r.id),
                };
              })
              .filter((pkg) => pkg.resources.length > 0);
            resolve();
          })
          .catch(() => {
            Vue.set(
              context.rootState.appState.status.resources,
              'failed',
              true,
            );
            reject();
          })
          .finally(() => {
            Vue.set(
              context.rootState.appState.status.resources,
              'loading',
              false,
            );
          });
      });
    },
  },
};

export default resources;

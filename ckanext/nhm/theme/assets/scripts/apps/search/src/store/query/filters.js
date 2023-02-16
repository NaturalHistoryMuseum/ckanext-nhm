import * as d3 from 'd3-collection';
import Vue from 'vue';
import shortid from 'shortid';
import { camelCase } from '../utils';
import staticPresets from './presets/static';
import dynamicPresets from './presets/dynamic';

let initialFilters = {
  group_root: {
    parent: null,
    key: 'and',
    content: [],
    id: 'root',
    display: {
      name: '',
      hidden: false,
      temp: false,
    },
  },
};

let filters = {
  namespaced: true,
  modules: {
    staticPresets,
    dynamicPresets,
  },
  state: {
    items: { ...initialFilters },
    parsingError: null,
  },
  getters: {
    count: (state) => (ignoreTemp) => {
      return d3
        .entries(state.items)
        .filter((c) => (ignoreTemp ? !c.value.display.temp : true)).length;
    },
    getFilterById: (state) => (id) => {
      return state.items[id];
    },
    getChildren: (state) => (id, asArray) => {
      let children = d3
        .entries(state.items)
        .filter((f) => f.value.parent === id);
      if (asArray) {
        return children;
      } else {
        return d3
          .nest()
          .key((d) => d.key)
          .rollup((d) => d[0].value)
          .object(children);
      }
    },
    getNestLevel: (state, getters) => (id) => {
      let filter = getters.getFilterById(id);
      let nestLevel = 0;
      while (filter.parent !== null) {
        nestLevel++;
        filter = getters.getFilterById(filter.parent);
      }
      return nestLevel;
    },
    queryfy: (state, getters) => (id, ignoreTemp) => {
      let data = state.items[id];
      let queryData = {};
      let isGroup = id.startsWith('group_');
      if (!isGroup) {
        queryData[data.key] = data.content;
      } else {
        let children = getters
          .getChildren(id, true)
          .filter((c) => (ignoreTemp ? !c.value.display.temp : true));
        if (children.length > 0) {
          let childData = children
            .map((c) => getters.queryfy(c.key, ignoreTemp))
            .filter((c) => c !== undefined);
          if (childData.length > 0) {
            queryData[data.key] = childData;
          }
        } else {
          return;
        }
      }
      return queryData;
    },
    hasFilter: (state) => (payload) => {
      // TODO: check for equality in a better/more consistent way
      let filterContent = JSON.stringify(payload.content);
      return d3.values(state.items).some((i) => {
        return (
          payload.parent === i.parent &&
          payload.key === i.key &&
          filterContent === JSON.stringify(i.content)
        );
      });
    },
    presets: (state, getters) => {
      return $.extend(
        getters['staticPresets/presets'],
        getters['dynamicPresets/presets'],
      );
    },
    temporaryFilters: (state) => {
      return d3.entries(state.items).filter((f) => f.value.display.temp);
    },
  },
  mutations: {
    changeKey(state, payload) {
      Vue.set(state.items[payload.id], 'key', payload.key);
    },
    changeContent(state, payload) {
      Vue.set(state.items[payload.id], 'content', payload.content);
    },
    changeName(state, payload) {
      Vue.set(state.items[payload.id].display, 'name', payload.name);
    },
    deleteFilter(state, filterId) {
      if (state.items[filterId].parent === null) {
        return;
      }
      Vue.delete(state.items, filterId);
    },
    resetFilters(state) {
      state.items = { ...initialFilters };
    },
    addFilter(state, payload) {
      let newFilter = {
        parent: payload.parent,
        key: payload.key,
        content: payload.content,
        id: payload.id || shortid.generate(),
        display: {
          name: payload.display.name || '',
          hidden: payload.display.hidden || false,
          temp: payload.display.temp || false,
        },
      };

      let filterKey;
      if (newFilter.display.name !== '') {
        filterKey = camelCase(newFilter.display.name);
      } else {
        filterKey = newFilter.id;
      }
      let filterName = `${payload.type}_${filterKey}`;
      Vue.set(state.items, filterName, newFilter);
    },
  },
  actions: {
    addGroup(context, payload) {
      payload.display = payload.display || {};
      let newGroup = {
        parent: payload.parent,
        key: 'and',
        content: [],
        id: payload.id || shortid.generate(),
        type: 'group',
        display: {
          name: payload.display.name || '',
          hidden: payload.display.hidden || false,
          temp: payload.display.temp || false,
        },
      };
      context.commit('addFilter', newGroup);
    },
    addTerm(context, payload) {
      payload.display = payload.display || {};
      let newTerm = {
        parent: payload.parent,
        key: payload.key,
        content: payload.content,
        id: payload.id || shortid.generate(),
        type: 'term',
        display: {
          name: payload.display.name || '',
          hidden: payload.display.hidden || false,
          temp: payload.display.temp || false,
        },
      };
      context.commit('addFilter', newTerm);
    },
    addPreset(context, payload) {
      let preset;
      if (context.getters['staticPresets/keys'].includes(payload.key)) {
        preset = context.state.staticPresets[payload.key].content;
      } else if (context.getters['dynamicPresets/keys'].includes(payload.key)) {
        let presetDetails = context.state.dynamicPresets[payload.key];
        let args = {};
        presetDetails.args.state.forEach((s) => {
          args[s] = context.rootState[s];
        });
        presetDetails.args.getters.forEach((g) => {
          args[g] = context.rootGetters[g];
        });
        preset = context.getters[`dynamicPresets/${payload.key}`](args);
      } else {
        return;
      }

      payload.display = payload.display || {};
      let currentParent = payload.parent;
      let somethingAdded = false;
      preset.forEach((p) => {
        let newFilter = {
          parent: currentParent,
          key: p.key,
          content: p.content,
          type: p.type,
          id: shortid.generate(),
          display: {
            hidden: payload.display.hidden || false,
            temp: payload.display.temp || false,
          },
        };
        if (p.display && p.display.name) {
          newFilter.display.name = p.display.name;
        }

        if (!context.getters.hasFilter(newFilter)) {
          context.commit('addFilter', newFilter);
          somethingAdded = true;
        }

        if (p.type === 'group') {
          currentParent = `group_${newFilter.id}`;
        }
      });

      return somethingAdded;
    },
    deleteTemporaryFilters(context) {
      let deleteCount = 0;
      d3.entries(context.state.items)
        .filter((f) => f.value.display.temp)
        .forEach((f) => {
          context.commit('deleteFilter', f.key);
          deleteCount++;
        });
      return deleteCount;
    },
    setFromQuery(context, query) {
      let currentState = { ...context.state.items };
      try {
        if (query.filters === undefined) {
          context.state.items = { ...initialFilters };
        } else {
          let dequeryfy = (items, parent) => {
            let itemList = {};
            items.forEach((i) => {
              let item = d3.entries(i)[0];
              if (
                Array.isArray(item.value) &&
                context.rootState.schema.groups.includes(item.key)
              ) {
                let groupId =
                  parent === null
                    ? 'group_root'
                    : `group_${shortid.generate()}`;
                itemList[groupId] = {
                  parent: parent,
                  key: item.key,
                  content: [],
                  display: {},
                };
                d3.entries(dequeryfy(item.value, groupId)).forEach((f) => {
                  itemList[f.key] = f.value;
                });
              } else {
                itemList[`term_${shortid.generate()}`] = {
                  parent: parent,
                  key: item.key,
                  content: item.value,
                  display: {},
                };
              }
            });
            return itemList;
          };

          let dequeried = dequeryfy([query.filters], null);
          context.state.items = { ...dequeried };
        }
        context.state.parsingError = null;
      } catch (e) {
        context.state.parsingError = e;
        // revert back to previous state
        context.state.items = { ...currentState };
      }
    },
  },
};

export default filters;

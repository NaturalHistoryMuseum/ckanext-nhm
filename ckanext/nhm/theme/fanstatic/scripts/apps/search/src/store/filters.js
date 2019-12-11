import Vue from 'vue';
import * as d3 from 'd3-collection';
import shortid from 'shortid';
import presets from './presets';

let initialFilters = {
    group_1: {
        parent:  null,
        key:     'and',
        content: []
    }
};

function dequeryfy(items, parent) {
    let itemList = {};
    items.forEach((i) => {
        let item = d3.entries(i)[0];
        if (Array.isArray(item.value)) {
            let groupId       = parent === null ? 'group_1' : `group_${shortid.generate()}`;
            itemList[groupId] = {
                parent:  parent,
                key:     item.key,
                content: []
            };
            d3.entries(dequeryfy(item.value, groupId)).forEach((f) => {
                itemList[f.key] = f.value;
            });
        }
        else {
            itemList[`term_${shortid.generate()}`] = {
                parent:  parent,
                key:     item.key,
                content: item.value
            }
        }
    });
    return itemList;
}

let filters = {
    namespaced: true,
    state:      {
        items: initialFilters
    },
    getters:    {
        getFilterById: (state) => (id) => {
            return state.items[id];
        },
        getChildren:   (state) => (id, asArray) => {
            let children = d3.entries(state.items)
                             .filter(f => f.value.parent === id);
            if (asArray) {
                return children;
            }
            else {
                return d3.nest()
                         .key(d => d.key)
                         .rollup(d => d[0].value)
                         .object(children);
            }
        },
        getNestLevel:  (state, getters) => (id) => {
            let filter    = getters.getFilterById(id);
            let nestLevel = 0;
            while (filter.parent !== null) {
                nestLevel++;
                filter = getters.getFilterById(filter.parent);
            }
            return nestLevel;
        },
        queryfy:       (state, getters) => (id) => {
            let data      = state.items[id];
            let queryData = {};
            let isGroup   = id.startsWith('group_');
            if (!isGroup) {
                queryData[data.key] = data.content;
            }
            else {
                queryData[data.key] = getters.getChildren(id, true)
                                             .map(c => getters.queryfy(c.key));
            }
            return queryData;
        },
        presetKeys:    () => {
            return d3.nest()
                     .key(p => p.key)
                     .rollup(p => p[0].value.name)
                     .object(d3.entries(presets));
        },
        hasTerm:       (state) => (termPayload) => {
            return d3.values(state.items).some(i => JSON.stringify(i) === JSON.stringify(termPayload))
        }
    },
    mutations:  {
        setFromQuery(state, query) {
            if (query.filters === undefined) {
                state.items = {...initialFilters};
            }
            else {
                let dequeried = dequeryfy([query.filters], null);
                state.items   = {...dequeried};
            }

        },
        changeKey(state, payload) {
            Vue.set(state.items[payload.id], 'key', payload.key);
        },
        changeContent(state, payload) {
            Vue.set(state.items[payload.id], 'content', payload.content);
        },
        deleteFilter(state, filterId) {
            if (state.items[filterId].parent === null) {
                return;
            }
            Vue.delete(state.items, filterId)
        },
        resetFilters(state) {
            state.items = {...initialFilters};
        },
        addGroup(state, parent) {
            let newGroup = {
                parent:  parent,
                key:     'and',
                content: []
            };
            Vue.set(state.items, `group_${shortid.generate()}`, newGroup);
        },
        addTerm(state, payload) {
            Vue.set(state.items, `term_${shortid.generate()}`, payload)
        },
        addPreset(state, payload) {
            let presetTerm = presets[payload.key];
            let newTerm    = {
                parent:  payload.parent,
                key:     presetTerm.key,
                content: presetTerm.content
            };
            Vue.set(state.items, `term_${shortid.generate()}`, newTerm)
        }
    }
};

export default filters;
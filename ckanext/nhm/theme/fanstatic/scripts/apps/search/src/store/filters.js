import Vue from 'vue';
import * as d3 from 'd3-collection';
import shortid from 'shortid';

let initialFilters = {
    group_1: {
        parent:  null,
        key:     'and',
        content: []
    },
    // term_1:  {
    //     parent:  'group_1',
    //     key:     'string_contains',
    //     content: {
    //         fields: ['genus'],
    //         value:  'helix'
    //     }
    // }
};

function dequeryfy(items, parentId) {
    let itemList = {};
    items.forEach((i) => {
        let item = d3.entries(i)[0];
        if (Array.isArray(item.value)) {
            let groupId       = parentId === null ? 'group_1' : `group_${shortid.generate()}`;
            itemList[groupId] = {
                parent:  parentId,
                key:     item.key,
                content: []
            };
            d3.entries(dequeryfy(item.value, groupId)).forEach((f) => {
                itemList[f.key] = f.value;
            });
        }
        else {
            itemList[`term_${shortid.generate()}`] = {
                parent:  parentId,
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
    },
    mutations:  {
        setFromQuery(state, query) {
            if (query.filters === undefined) {
                state.items = {...initialFilters};
            }
            else {
                let dequeried = dequeryfy([query.filters], null);
                state.items = {...dequeried};
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
        addGroup(state, parentId) {
            let newGroup = {
                parent:  parentId,
                key:     'and',
                content: []
            };
            Vue.set(state.items, `group_${shortid.generate()}`, newGroup);
        },
        addTerm(state, payload) {
            let newTerm = {
                parent:  payload.parentId,
                key:     payload.key,
                content: payload.content
            };
            Vue.set(state.items, `term_${shortid.generate()}`, newTerm)
        }
    }
};

export default filters;
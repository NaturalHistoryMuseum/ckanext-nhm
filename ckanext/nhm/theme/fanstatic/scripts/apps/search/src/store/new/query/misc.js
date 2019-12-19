let misc = {
    namespaced: false,
    state:      {
        search: '',
        after:  null
    },
    mutations:  {
        setSearch(state, searchString) {
            state.search = searchString;
        },
    }
};

export default misc;
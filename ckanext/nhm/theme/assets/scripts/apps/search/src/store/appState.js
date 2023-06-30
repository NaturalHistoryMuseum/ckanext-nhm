let appState = {
  namespaced: true,
  state: {
    app: {
      loading: false,
      error: false,
    },
    query: {
      parsingError: {
        unknown: false,
        resourceIds: null,
        queryBody: null,
      },
    },
    status: {
      resultData: {
        loading: false,
        failed: false,
        promise: null,
      },
      slug: {
        loading: false,
        failed: false,
        promise: null,
      },
      slugEdit: {
        loading: false,
        failed: false,
        promise: null,
      },
      doi: {
        loading: false,
        failed: false,
        promise: null,
      },
      download: {
        loading: false,
        failed: false,
        promise: null,
      },
      resources: {
        loading: false,
        failed: false,
        promise: null,
      },
      queryEdit: {
        loading: false,
        failed: false,
        promise: null,
      },
    },
  },
  getters: {
    app: (state) => {
      return {
        loading: state.app.loading || state.status.resources.loading,
        failed: state.app.error || state.status.resources.failed,
      };
    },
  },
};

export default appState;

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
        promise: new Promise((resolve) => setTimeout(resolve, 1000)),
      },
      slug: {
        loading: false,
        failed: false,
        promise: new Promise((resolve) => setTimeout(resolve, 1000)),
      },
      slugEdit: {
        loading: false,
        failed: false,
        promise: new Promise((resolve) => setTimeout(resolve, 1000)),
      },
      doi: {
        loading: false,
        failed: false,
        promise: new Promise((resolve) => setTimeout(resolve, 1000)),
      },
      download: {
        loading: false,
        failed: false,
        promise: new Promise((resolve) => setTimeout(resolve, 1000)),
      },
      resources: {
        loading: false,
        failed: false,
        promise: new Promise((resolve) => setTimeout(resolve, 1000)),
      },
      queryEdit: {
        loading: false,
        failed: false,
        promise: new Promise((resolve) => setTimeout(resolve, 1000)),
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

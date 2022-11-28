let appState = {
    namespaced: true,
    state:      {
        app:     {
            loading: false,
            error:   false
        },
        query:   {
            parsingError: {
                unknown:     false,
                resourceIds: null,
                queryBody:   null
            }
        },
        status: {
            resultData: {
                loading: false,
                failed:  false
            },
            slug:       {
                loading: false,
                failed:  false
            },
            slugEdit: {
                loading: false,
                failed:  false
            },
            doi:        {
                loading: false,
                failed:  false
            },
            download:   {
                loading: false,
                failed:  false
            },
            resources: {
                loading: false,
                failed: false
            },
            queryEdit: {
                loading: false,
                failed: false
            }
        }
    },
    getters: {
        app: (state) => {
            return {
                loading: state.app.loading || state.status.resources.loading,
                failed: state.app.error || state.status.resources.failed
            }
        }
    }
}

export default appState;

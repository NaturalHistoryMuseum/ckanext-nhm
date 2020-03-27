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
            doi:        {
                loading: false,
                failed:  false
            },
            download:   {
                loading: false,
                failed:  false
            }
        }
    }
}

export default appState;
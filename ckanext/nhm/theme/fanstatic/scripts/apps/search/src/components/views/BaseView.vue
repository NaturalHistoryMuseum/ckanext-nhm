<template>
    <pre>
        {{ $store.state.results.current.result }}
    </pre>
</template>

<script>
    import {mapGetters, mapState, mapMutations} from 'vuex';

    export default {
        name:     'BaseView',
        data:     function () {
            return {
                showFields:    false
            }
        },
        mounted:  function () {
            this.updateView();
        },
        computed: {
            ...mapState('results', ['current', 'headers', 'page']),
            ...mapGetters('constants', ['resourceDetails']),
            ...mapGetters('results', ['total', 'records'])
        },
        methods:  {
            ...mapMutations('results', ['removeHeader', 'moveHeader']),
            getDetails(resourceId) {
                let resourceDetails = this.resourceDetails[resourceId];

                let packageUrl  = `/dataset/${resourceDetails.package_id}`;
                let resourceUrl = packageUrl + `/resource/${resourceDetails.id}`;

                return {
                    packageUrl,
                    resourceUrl,
                    titleField: resourceDetails.raw._title_field || '_id',
                    imageField: resourceDetails.raw._image_field
                }
            },
            getImage(item) {
                if (item.resource === '05ff2255-c38a-40c9-b657-4ccb55ab2feb') {
                    try {
                        return item.data.associatedMedia[0].identifier.replace('preview', 'thumbnail');
                    }
                    catch (e) {
                        return null;
                    }
                }
                else {
                    try {
                        return item.data[this.getDetails(item.resource).imageField][0];
                    }
                    catch (e) {
                        return null;
                    }
                }
            },
            getValue(item, field) {
                let v = {...item};
                let subFields = field.split('.');

                let subItems = (parentItem, subField) => {
                    if (Array.isArray(parentItem)) {
                        return parentItem.map(x => subItems(x, subField)).join('; ');
                    }
                    else {
                        return parentItem[subField];
                    }
                };

                for (let i = 0; i < subFields.length; i++) {
                    try {
                        v = subItems(v, subFields[i])
                    }
                    catch (e) {
                        break;
                    }
                }
                return v;
            },
            updateView() {
                //
            }
        },
        watch:    {
            current: {
                handler() {
                    this.updateView();
                },
                deep: true
            }
        }
    }
</script>
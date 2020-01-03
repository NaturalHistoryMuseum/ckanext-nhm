<template>
    <pre>
        {{ resultData.result }}
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
            ...mapState('results', ['resultData', 'page']),
            ...mapState('results/display', ['headers']),
            ...mapGetters('results', ['total', 'records']),
            ...mapGetters('results/query/resources', ['resourceDetails'])
        },
        methods:  {
            ...mapMutations('results/display', ['removeHeader', 'moveHeader']),
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
            getImages(item, first) {
                let images;
                if (item.data.associatedMedia !== undefined) {
                    try {
                        images = item.data.associatedMedia.map(i => {
                            return {preview: i.identifier, thumb: i.identifier.replace('preview', 'thumbnail')};
                        });
                    }
                    catch (e) {
                        images = [];
                    }
                }
                else {
                    try {
                        images = item.data[this.getDetails(item.resource).imageField].map(i => {
                            return {preview: i, thumb: i}
                        });
                    }
                    catch (e) {
                        images = [];
                    }
                }

                if (first) {
                    return images.length > 0 ? images[0] : null;
                }
                else {
                    return images;
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
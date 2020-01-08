<template>
    <pre>
        {{ resultData.result }}
    </pre>
</template>

<script>
    import {mapGetters, mapMutations, mapState} from 'vuex';

    export default {
        name:     'BaseView',
        data:     function () {
            return {
                showFields: false
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
                    imageField: resourceDetails.raw._image_field,
                    imageDelimiter: resourceDetails.raw._image_delimiter || ''
                }
            },
            getImages(item, first) {
                let images;
                if (item.data.associatedMedia !== undefined) {
                    try {
                        images = item.data.associatedMedia.map((img) => {
                            return {
                                preview: img.identifier,
                                thumb:   img.identifier.replace('preview', 'thumbnail'),
                                title:   img.title,
                                id:      img.assetId
                            };
                        });
                    } catch (e) {
                        images = [];
                    }
                }
                else {
                    try {
                        let resourceDetails = this.getDetails(item.resource);
                        let imageFieldValue = item.data[resourceDetails.imageField];
                        if (resourceDetails.imageDelimiter !== '') {
                            images = imageFieldValue.split(resourceDetails.imageDelimiter);
                        }
                        else {
                            images = [imageFieldValue]
                        }
                        images = images.map((img, ix) => {
                            return {
                                preview: img,
                                thumb:   img,
                                title:   '',
                                id:      `${item.data._id}_${ix}`
                            }
                        });
                    } catch (e) {
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
                let v         = {...item};
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
                    } catch (e) {
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
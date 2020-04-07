<template>
    <pre>
        {{ resultData.result }}
    </pre>
</template>

<script>
    import {mapGetters, mapMutations, mapState} from 'vuex';
    import axios from 'axios';
    import SparkMD5 from 'spark-md5';

    export default {
        name:     'BaseView',
        data:     function () {
            return {
                showFields: false
            }
        },
        computed: {
            ...mapState('results', ['resultData', 'page']),
            ...mapState('results/display', ['headers']),
            ...mapGetters('results', ['total', 'records']),
            ...mapGetters('results/display', ['licenceFromId']),
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
                    titleField:     resourceDetails.raw._title_field || '_id',
                    imageField:     resourceDetails.raw._image_field,
                    imageDelimiter: resourceDetails.raw._image_delimiter || '',
                    imageLicence:   this.licenceFromId(resourceDetails.raw._image_licence)
                }
            },
            getImages(item, first) {
                let images;
                const noImageSize = 1164;
                const noImageHash = 'b67da4c749bc536ddf27339cb0ec4e63';


                let resourceDetails = this.getDetails(item.resource);

                if (item.data.associatedMedia !== undefined) {
                    try {
                        images = item.data.associatedMedia.map((img) => {
                            let imgLicence = img.license === resourceDetails.imageLicence.url ?
                                resourceDetails.imageLicence :
                                {title: img.license, url: img.license};
                            let imgThumb   = img.identifier.replace('preview', 'thumbnail');
                            let isBroken   = false;
                            axios.get(imgThumb.replace('media-store', 'media-store1'), {responseType: 'blob'}).then(d => {
                                if (d.data.size === noImageSize) {
                                    console.log(imgThumb)
                                    let fileReader       = new FileReader();
                                    fileReader.onloadend = function () {
                                        let imageHash = SparkMD5.ArrayBuffer.hash(fileReader.result);
                                        isBroken = imageHash === noImageHash;
                                        if (!isBroken) {
                                            console.log(imageHash)
                                        }
                                    }
                                    fileReader.readAsArrayBuffer(d.data);
                                }
                            }).catch(e => {
                                console.log(e)
                            })
                            return {
                                preview:  img.identifier,
                                thumb:    imgThumb,
                                title:    img.title,
                                id:       img.assetID,
                                licence:  imgLicence,
                                isBroken: isBroken
                            };
                        });
                    } catch (e) {
                        images = [];
                    }
                }
                else {
                    try {
                        let imageFieldValue = item.data[resourceDetails.imageField];
                        if (imageFieldValue === undefined) {
                            images = [];
                        }
                        else if (resourceDetails.imageDelimiter !== '') {
                            images = imageFieldValue.split(resourceDetails.imageDelimiter);
                        }
                        else {
                            images = [imageFieldValue]
                        }
                        images = images.map((img, ix) => {
                            return {
                                preview:  img,
                                thumb:    img,
                                title:    item.data[resourceDetails.titleField],
                                id:       `${item.data._id}_${ix}`,
                                licence:  resourceDetails.imageLicence,
                                isBroken: false
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
            }
        }
    }
</script>
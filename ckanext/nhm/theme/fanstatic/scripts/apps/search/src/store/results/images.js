import axios from 'axios';
import SparkMD5 from 'spark-md5';

let images = {
    namespaced: true,
    getters:    {
        getItemImages: (state, getters, rootState, rootGetters) => (item, first, recordIndex) => {
            let images;
            const noImageSize = 1164;
            const noImageHash = 'b67da4c749bc536ddf27339cb0ec4e63';

            let resourceDetails = rootGetters['results/query/resources/resourceDetails'][item.resource];
            let recordUrl       = `${resourceDetails.resourceUrl}/record/${item.data._id}`;
            let recordTitle     = item.data[resourceDetails.titleField] || item.data._id;

            if (item.data.associatedMedia !== undefined) {
                try {
                    images = item.data.associatedMedia.map((img) => {
                        let imgLicence = img.license === resourceDetails.imageLicence.url ?
                            resourceDetails.imageLicence :
                            {title: img.license, url: img.license};
                        let imgThumb   = img.identifier.replace('preview', 'thumbnail');
                        let isBroken   = false;
                        axios.get(imgThumb.replace('media-store', 'media-store1'), {responseType: 'blob'})
                             .then(d => {
                                 if (d.data.size === noImageSize) {
                                     console.log(imgThumb)
                                     let fileReader       = new FileReader();
                                     fileReader.onloadend = function () {
                                         let imageHash = SparkMD5.ArrayBuffer.hash(fileReader.result);
                                         isBroken      = imageHash === noImageHash;

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


            images = images.map((i, iix, ia) => {
                return {
                    record:           item,
                    image:            i,
                    recordImageIndex: iix,
                    recordIndex:      recordIndex,
                    imageTotal:       ia.length,
                    recordUrl,
                    recordTitle
                }
            })

            if (first) {
                return images.length > 0 ? images[0] : null;
            }
            else {
                return images;
            }
        },
    }
}

export default images;
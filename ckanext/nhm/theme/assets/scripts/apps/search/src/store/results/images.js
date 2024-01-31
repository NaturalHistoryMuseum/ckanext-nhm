import Vue from 'vue';

let images = {
  namespaced: true,
  state: {
    imageRecords: [],
    locked: false,
  },
  getters: {
    loadedImageRecords: (state) => {
      let loadedImgRecords = state.imageRecords.filter(
        (r) => r.image.canLoad && !r.image.loading,
      );
      loadedImgRecords.sort((a, b) => {
        const recordOrder = a.recordIndex - b.recordIndex;
        return recordOrder === 0
          ? a.recordImageIndex - b.recordImageIndex
          : recordOrder;
      });
      return loadedImgRecords;
    },
    getItemImages:
      (state, getters, rootState, rootGetters) =>
      (item, first, recordIndex) => {
        /* gets the images from a single record */

        let images;

        // details of the resource this record is from
        let resourceDetails =
          rootGetters['results/query/resources/resourceDetails'][item.resource];

        // for convenience
        let recordUrl = `${resourceDetails.resourceUrl}/record/${item.data._id}`;
        let recordTitle =
          item.data[resourceDetails.titleField] || item.data._id;

        // define the image object
        let defaultImg = {
          download: null,
          preview: null,
          thumb: null,
          title: recordTitle,
          id: null,
          licence: resourceDetails.imageLicence,
          loading: true,
          canLoad: false,
        };

        // specimen collections and index lots have a special media field
        if (item.data.associatedMedia !== undefined) {
          try {
            images = item.data.associatedMedia.map((img) => {
              let imgRecord = { ...defaultImg };
              imgRecord.download = `${img.identifier}/original`;
              imgRecord.preview = `${img.identifier}/preview`;
              imgRecord.thumb = `${img.identifier}/thumbnail`;
              imgRecord.title = img.title || imgRecord.title;
              imgRecord.id = img.identifier;
              imgRecord.licence =
                img.license === resourceDetails.imageLicence.url
                  ? resourceDetails.imageLicence
                  : { title: img.license, url: img.license };
              return imgRecord;
            });
          } catch (e) {
            images = [];
          }
        }

        // everything else just uses a URL or a list of URLs in a string field
        else {
          try {
            let imageFieldValue = item.data[resourceDetails.imageField];
            if (imageFieldValue === undefined) {
              images = [];
            } else if (resourceDetails.imageDelimiter !== '') {
              images = imageFieldValue.split(resourceDetails.imageDelimiter);
            } else {
              images = [imageFieldValue];
            }
            images = images.map((img, ix) => {
              let imgRecord = { ...defaultImg };
              imgRecord.download = img;
              imgRecord.preview = img;
              imgRecord.thumb = img;
              imgRecord.id = `${item.data._id}_${ix}`;
              return imgRecord;
            });
          } catch (e) {
            images = [];
          }
        }

        images = images.map((i, iix, ia) => {
          return {
            record: item,
            image: i,
            recordImageIndex: iix,
            recordIndex: recordIndex,
            imageTotal: ia.length,
            recordUrl,
            recordTitle,
          };
        });

        if (first) {
          return images.length > 0 ? images[0] : null;
        } else {
          return images;
        }
      },
  },
  actions: {
    loadAndCheckImages(context, searchId) {
      const isAborted = context.rootGetters['results/isAborted'];
      Vue.set(context.state, 'imageRecords', []);
      if (context.state.locked) {
        return;
      } else {
        Vue.set(context.state, 'locked', true);
      }

      // remove current page images
      context.commit('results/display/addPageImages', [], { root: true });

      let imgRecords = [];

      let records = context.rootGetters['results/records'];

      records.forEach((r, rix) => {
        context.getters.getItemImages(r, false, rix).forEach((i) => {
          imgRecords.push(i);
        });
      });

      function checkImageSrc(url) {
        // using a requests library like axios doesn't work if the external server
        // doesn't have CORS set up properly, and all we want to know is if it loads as
        // an image anyway
        return new Promise((resolve, reject) => {
          let imageElement = new Image();
          imageElement.onload = () => {
            let ratio = imageElement.width / imageElement.height;
            resolve(ratio);
          };
          imageElement.onerror = reject;
          if (isAborted(searchId)) {
            // don't try and load if this request has been aborted
            reject();
          } else {
            // this starts the loading test
            imageElement.src = url;
          }
        });
      }

      let brokenChecks = imgRecords.map((r) => {
        return checkImageSrc(r.image.thumb)
          .then((ratio) => {
            r.image.canLoad = true;
            r.image.ratio = ratio;
          })
          .catch(() => {
            r.image.canLoad = false;
            r.image.ratio = 1;
          })
          .finally(() => {
            r.image.loading = false;
            if (!isAborted(searchId)) {
              // only add to the state if the search is still ongoing
              context.state.imageRecords.push(r);
            }
          });
      });
      return Promise.allSettled(brokenChecks).then(() => {
        return new Promise((resolve) => {
          if (isAborted(searchId)) {
            // remove everything already added to the state
            Vue.set(context.state, 'imageRecords', []);
          }
          context.commit(
            'results/display/addPageImages',
            context.getters.loadedImageRecords,
            { root: true },
          );
          Vue.set(context.state, 'locked', false);
          resolve();
        });
      });
    },
  },
};

export default images;

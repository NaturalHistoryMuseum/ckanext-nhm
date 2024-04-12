import { defineStore } from 'pinia';
import { computed, ref, toRaw } from 'vue';
import { get, post } from '../utils/api';
import { useRepo } from 'pinia-orm';
import { Image, Record, Resource } from '../utils/models';
import { emitter, events } from '../utils/events';
import { cyrb53 } from '../utils/misc';

export const useStore = defineStore('liv', () => {
  // repos
  const resourceRepo = computed(() => useRepo(Resource));
  const recordRepo = computed(() => useRepo(Record));
  const imageRepo = computed(() => useRepo(Image));

  // internal constants
  const pageSize = 100;
  const bufferSize = 10;

  // current query
  const query = ref({});
  const imageQuery = ref({}); // secondary filters for images within records
  const currentResources = computed(() => {
    return resourceRepo.value
      .where((r) => query.value.resource_ids.includes(r.id))
      .get();
  });
  const queryHash = computed(() => {
    return cyrb53(JSON.stringify(query.value));
  });

  // current request
  const requestQuery = ref(null);
  const request = ref(null);
  const after = ref(null);
  const _done = ref(false);
  const pending = ref(false);
  const more = computed(() => {
    return request.value != null && !_done.value;
  });
  const requestedImgs = ref(0);
  const failedImgs = ref(0);
  const disableAutoLoad = computed(() => {
    if (requestedImgs.value < bufferSize) {
      return false;
    }
    return failedImgs.value / requestedImgs.value > 0.5;
  });

  // current image/record
  const currentImage = ref(null);
  const currentRecord = computed(() => {
    if (currentImage.value == null) {
      return null;
    } else {
      return recordRepo.value
        .withAllRecursive()
        .find(currentImage.value.recordId);
    }
  });

  // results
  const totalRecords = ref(0);
  const allImages = computed(() => {
    return imageRepo.value.withAllRecursive(2).get();
  });
  const allRecords = computed(() => {
    return recordRepo.value.withAll().get();
  });

  // state
  const state = ref({
    attempted: false,
    loading: false,
    error: false,
    errorMsg: null,
  });
  const showOverlay = ref(false);

  // api/request functions
  async function addImageFilters(newQuery) {
    let imageFields = [];
    let promises = [];

    function _addImgField(resourceModel) {
      if (
        resourceModel.imgField &&
        !imageFields.includes(resourceModel.imgField)
      ) {
        imageFields.push(resourceModel.imgField);
      }
    }

    if (newQuery.resource_ids == null || newQuery.resource_ids.length === 0) {
      promises.push(
        getAllResources().then(() => {
          return resourceRepo.value.all().forEach(_addImgField);
        }),
      );
    } else {
      promises = newQuery.resource_ids.map((rid) => {
        return get('resource_show', { id: rid }).then((data) => {
          let resModel = addResource(data.result);
          if (resModel) {
            _addImgField(resModel);
          }
        });
      });
    }
    return Promise.allSettled(promises).then(() => {
      const term = { exists: { fields: imageFields } };
      if (!newQuery.query) {
        newQuery.query = {};
      }
      if (!newQuery.query.filters) {
        newQuery.query.filters = {
          and: [term],
        };
      } else if (Object.keys(newQuery.query.filters)[0] !== 'and') {
        const existingFilters = { ...newQuery.query.filters };
        newQuery.query.filters = {
          and: [term, existingFilters],
        };
      } else {
        let jsonTerm = JSON.stringify(term);
        if (
          !newQuery.query.filters.and
            .map((t) => JSON.stringify(t))
            .some((t) => t === jsonTerm)
        ) {
          newQuery.query.filters.and.push(term);
        }
      }
      return newQuery;
    });
  }

  async function* multisearch() {
    while (true) {
      const json = await post('datastore_multisearch', requestQuery.value);
      totalRecords.value = json.result.total;
      yield* json.result.records;
      if (json.result.after) {
        requestQuery.value.after = json.result.after;
      } else {
        break;
      }
    }
  }

  async function getRecords(batches = 1) {
    state.value.loading = true;
    state.value.attempted = true;
    pending.value = true;

    // make a copy of the current query hash so requests can use it as an abort signal
    const qH = queryHash.value.toString();

    return new Promise(async (resolve, reject) => {
      if (request.value == null) {
        request.value = multisearch();
      }

      let imageRequests = [];

      let batchSize = bufferSize * batches;
      let i = 0;
      while (!_done.value && (batchSize ? i < batchSize : true)) {
        imageRequests.push(
          request.value
            .next()
            .then((next) => {
              if (next.done) {
                _done.value = true;
              }
              return addRecordAndImages(next.value, qH);
            })
            .catch((e) => {
              // this doesn't currently do anything other than store the error
              state.value.error = true;
              state.value.errorMsg = e;
            }),
        );
        i++;
      }

      Promise.allSettled(imageRequests).then(() => {
        pending.value = false;
        if (imageRequests.length > 0) {
          // only emit if records were actually retrieved
          emitter.emit(events.recordsRetrieved, {});
        }
        state.value.loading = false;
        resolve();
      });
    });
  }

  function addRecordAndImages(recordData, qH) {
    const recordIIIF = recordData.iiif ? recordData.iiif.items : [];
    if (recordIIIF.length === 0) {
      console.error('No IIIF data.');
      console.log(recordData);
      return new Promise((r) => r());
    }

    const resource = resourceRepo.value.find(recordData.resource);
    const recordId = `${recordData.resource}_${recordData.data._id}`;
    const record = {
      id: recordId,
      data: toRaw(recordData.data),
      manifest: recordData.iiif.id,
      resourceId: recordData.resource,
      images: [],
    };

    const imageRequests = recordIIIF.map((img, ix) => {
      requestedImgs.value++;
      const imgUrl = img.items[0].items[0].body.id;
      const infoUrl = imgUrl + '/info.json';
      return get(infoUrl)
        .then((data) => {
          return new Promise((resolve) => {
            let recordImgData = {};
            if (resource && resource.dwc) {
              recordImgData = recordData.data.associatedMedia.filter(
                (m) => m.identifier === imgUrl,
              )[0];
            }

            let addImage = Object.entries(imageQuery.value).every((q) => {
              if (q[0] === 'ix') {
                return ix.toString() === q[1];
              }
              try {
                // get record value
                let keys = q[0].split('.');
                let val = recordImgData;
                for (const kIx in keys) {
                  val = val[keys[kIx]];
                }
                return q[1].includes(val);
              } catch (e) {
                return false;
              }
            });

            if (addImage) {
              record.images.push({
                id: `${recordData.resource}/${recordId}/${ix}`,
                ix,
                url: imgUrl,
                recordId: recordId,
                iiifData: data,
                data: recordImgData,
              });
            }
            resolve();
          });
        })
        .catch(() => {
          failedImgs.value++;
        });
    });

    return Promise.allSettled(imageRequests).then(() => {
      if (queryHash.value.toString() === qH) {
        // if it doesn't match, it's not from the current query
        recordRepo.value.save(record);
      }
    });
  }

  function addResource(resourceData, packageName) {
    if (!resourceData._image_field) {
      return;
    }
    const titleField = resourceData._title_field;
    const subtitleField = resourceData._subtitle_field;
    const imgField = resourceData._image_field;

    let config = {
      id: resourceData.id,
      name: resourceData.name,
      titleField: titleField,
      subtitleField: subtitleField,
      imgField: imgField,
      dwc: resourceData.format.toLowerCase() === 'dwc',
      data: resourceData,
      packageId: resourceData.package_id,
    };

    if (packageName) {
      config.packageName = packageName;
    }

    return resourceRepo.value.save(config);
  }

  function getAllResources() {
    return get('current_package_list_with_resources', {
      limit: 10000,
    }).then((data) => {
      data.result.forEach((p) => {
        p.resources.forEach((r) => addResource(r, p.title));
      });
    });
  }

  // mutators
  function changeImage(img) {
    currentImage.value = img;
    showOverlay.value = true;
  }

  function setQuery(newQuery, newImageQuery = null) {
    if (newImageQuery) {
      imageQuery.value = newImageQuery;
    } else {
      imageQuery.value = {};
    }
    query.value = newQuery;

    state.value = {
      attempted: false,
      loading: false,
      error: false,
      errorMsg: null,
    };
    requestedImgs.value = 0;
    failedImgs.value = 0;
    pending.value = false;
    after.value = null;
    _done.value = false;
    request.value = null;
    requestQuery.value = null;
    totalRecords.value = 0;
    recordRepo.value.flush();
    imageRepo.value.flush();
    addImageFilters(query.value).then((imgQuery) => {
      requestQuery.value = {
        ...imgQuery,
        size: pageSize,
      };
      emitter.emit(events.querySet, query.value);
      return getRecords(4);
    });
  }

  return {
    allImages,
    allRecords,
    changeImage,
    currentImage,
    currentRecord,
    currentResources,
    disableAutoLoad,
    getAllResources,
    getRecords,
    imageQuery,
    imageRepo,
    more,
    pending,
    query,
    queryHash,
    recordRepo,
    resourceRepo,
    setQuery,
    showOverlay,
    state,
    totalRecords,
  };
});

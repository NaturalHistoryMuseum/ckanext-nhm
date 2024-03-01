import { defineStore } from 'pinia';
import { computed, ref, toRaw, watch } from 'vue';
import { useStore } from './main';
import { emitter, events } from '../utils/events';
import { get, post } from '../utils/api';
import { useRepo } from 'pinia-orm';
import { Image, Record, Resource } from '../utils/models';
import { useRoute } from 'vue-router';

export const useModeStore = defineStore('modes', () => {
  // other stores
  const mainStore = useStore();

  // repos
  const resourceRepo = computed(() => useRepo(Resource));
  const recordRepo = computed(() => useRepo(Record));
  const imageRepo = computed(() => useRepo(Image));

  // mode setup
  const defaultModeConfig = new ModeConfig({
    id: 'default',
    externalUrl: '',
    enableResources: true,
    enableFilters: true,
  });
  const modeConfigs = [
    {
      id: 'image',
      externalUrl: 'image',
      paramCount: 1,
    },
    {
      id: 'resource',
      externalUrl: 'resource',
      paramCount: 1,
      enableFilters: true,
    },
    {
      id: 'record',
      externalUrl: 'record',
      paramCount: 2,
    },
    {
      id: 'recordImage',
      externalUrl: 'record',
      paramCount: 3,
    },
    {
      id: 'slug',
      externalUrl: 'search',
      paramCount: 1,
    },
    {
      id: 'doi',
      externalUrl: 'search',
      paramCount: 2,
    },
  ].map((c) => new ModeConfig(c));

  // state
  const route = useRoute();

  const mode = computed(() => {
    let isMode = !!route.params.mode;
    let modeName = isMode ? route.params.mode[0] : 'default';

    // validate by trying to retrieve a matching config
    let matching = modeConfigs.filter(
      (m) =>
        m.externalUrl === modeName && m.paramCount === modeParams.value.length,
    );
    if (matching.length > 0) {
      return matching[0];
    } else {
      return defaultModeConfig;
    }
  });

  const modeParams = computed(() => {
    let isMode = !!route.params.mode;
    return isMode ? route.params.mode.slice(1, route.params.mode.length) : [];
  });

  function loadData() {
    emitter.once(events.recordsRetrieved, () => {
      mainStore.currentImage = mainStore.allImages[0];
    });

    switch (mode.value.id) {
      case 'image':
        // no record information, just a single image
        mainStore.currentImage = mainStore.imageRepo.save({
          url: '/media/' + modeParams.value[0],
        });
        mainStore.showOverlay = true;
        break;
      case 'resource':
        // a whole resource
        resourceMode(modeParams.value[0]);
        break;
      case 'record':
        // all images within a record
        recordMode(modeParams.value[0], modeParams.value[1], null);
        break;
      case 'recordImage':
        // single image within a record
        recordMode(
          modeParams.value[0],
          modeParams.value[1],
          modeParams.value[2],
        );
        break;
      case 'slug':
        // a search slug
        slugMode(modeParams.value[0]);
        break;
      case 'doi':
        // a query doi
        doiMode(modeParams.value[0], modeParams.value[1]);
        break;
      default:
        defaultMode();
    }
  }

  function resourceMode(resourceId) {
    mainStore.setQuery({
      query: {},
      resource_ids: [resourceId],
    });
  }

  function recordMode(resourceId, recordId, imageId) {
    if (imageId != null) {
      emitter.once(events.recordsRetrieved, () => {
        mainStore.changeImage(mainStore.allImages[0]);
      });
    }
    mainStore.setQuery(
      {
        query: {
          filters: {
            and: [
              {
                string_equals: {
                  fields: ['_id'],
                  value: recordId,
                },
              },
            ],
          },
        },
        resource_ids: [resourceId],
      },
      imageId == null ? null : { ix: imageId },
    );
  }

  function slugMode(slug) {
    post('datastore_resolve_slug', { slug }).then((data) => {
      if (data.success) {
        mainStore.setQuery(data.result);
      }
    });
  }

  function doiMode(doiPrefix, doiSuffix) {
    post('datastore_resolve_slug', { slug: `${doiPrefix}/${doiSuffix}` }).then(
      (data) => {
        if (data.success) {
          mainStore.setQuery(data.result);
        }
      },
    );
  }

  function defaultMode() {
    mainStore.setQuery({
      query: {
        filters: {
          and: [
            {
              string_equals: {
                fields: ['associatedMedia.category'],
                value: 'Drawer scan',
              },
            },
          ],
        },
      },
      resource_ids: [
        '05ff2255-c38a-40c9-b657-4ccb55ab2feb',
        'bb909597-dedf-427d-8c04-4c02b3a24db3',
      ],
    });
  }

  return {
    mode,
    modeParams,
    loadData,
  };
});

class ModeConfig {
  constructor(config) {
    this.id = config.id;
    this.externalUrl = config.externalUrl;
    this.paramCount = config.paramCount == null ? 0 : config.paramCount;
    this.enableResources =
      config.enableResources == null ? false : config.enableResources;
    this.enableFilters =
      config.enableFilters == null ? false : config.enableFilters;
  }

  get lockAll() {
    return !this.enableResources && !this.enableFilters;
  }
}

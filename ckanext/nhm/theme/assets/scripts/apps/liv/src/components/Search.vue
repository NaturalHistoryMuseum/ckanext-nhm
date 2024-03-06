<template>
  <div :class="$style.main">
    <template v-if="modes.mode && modes.mode.enableFilters">
      <zoa-input
        zoa-type="textbox"
        label="Keywords"
        :options="{ placeholder: 'Search everything' }"
        v-model="searchEverything"
        :class="$style.input"
      />
      <template v-if="enableDwcFilters">
        <zoa-input
          zoa-type="textbox"
          label="Search taxa"
          :options="{ placeholder: 'e.g. coleoptera' }"
          v-model="taxa"
          :class="$style.input"
        />
        <zoa-input
          zoa-type="multiselect"
          label="Type status"
          :options="{ options: typeStatusOptions, enableSearch: true }"
          v-model="typeStatus"
          :class="$style.input"
        />
        <zoa-input
          zoa-type="multiselect"
          label="Image category"
          :options="{ options: imageCategoryOptions, enableSearch: true }"
          v-model="imageCategory"
          :class="$style.input"
        />
      </template>
    </template>
    <zoa-input
      zoa-type="multiselect"
      label="Resources"
      :options="{ options: resourceOptions, enableSearch: true }"
      v-model="resources"
      :class="$style.input"
      v-if="modes.mode && modes.mode.enableResources"
    />
    <div :class="$style.buttons">
      <zoa-button @click="clearAll">Clear</zoa-button>
      <zoa-button @click="applyFilters">Apply</zoa-button>
    </div>
  </div>
</template>

<script setup>
import { ZoaButton, ZoaInput } from '@nhm-data/zoa';
import { useModeStore, useStore } from '../store';
import { computed, onMounted, ref } from 'vue';
import { emitter, events } from '../utils/events';

// links to a show/hide so the hide can be triggered from inside this component
const model = defineModel();

const store = useStore();
const modes = useModeStore();

const searchEverything = ref(null);

const resources = ref([]);
const resourceOptions = computed(() => {
  return store.resourceRepo.all().map((r) => {
    return {
      label: r.name,
      value: r.id,
      group: r.packageName,
    };
  });
});
const resourceModels = computed(() => {
  return resources.value
    .map((r) => store.resourceRepo.find(r))
    .filter((r) => r != null);
});
const enableDwcFilters = computed(() => {
  return resourceModels.value.length > 0
    ? resourceModels.value.every((r) => {
        // this is a horrible hack to make it work for index lots as well, because it's *almost* dwc
        return r.dwc || r.id === 'bb909597-dedf-427d-8c04-4c02b3a24db3';
      })
    : false;
});

const taxa = ref(null);
const taxaFields = [
  'scientificName',
  'currentScientificName',
  'kingdom',
  'phylum',
  'class',
  'order',
  'family',
  'genus',
  'specificEpithet',
  'infraspecificEpithet',
  'higherClassification',
];

const typeStatus = ref([]);
const typeStatusOptions = ref([
  { value: 'Type', order: 0 },
  { value: 'Non-type', order: 1 },
  { value: 'Paratype', order: 2 },
  { value: 'Holotype', order: 3 },
  { value: 'Syntype', order: 4 },
  { value: 'Isotype', order: 5 },
  { value: 'Lectotype', order: 6 },
  { value: 'Paralectotype', order: 7 },
  { value: 'Original material', order: 8 },
  { value: 'Isolectotype', order: 9 },
  { value: 'Cotype', order: 10 },
  { value: 'Figured', order: 11 },
  { value: 'Isosyntype', order: 12 },
]);

const imageCategory = ref([]);
const imageCategoryOptions = ref([
  { value: 'Drawer scan', order: 0 },
  { value: 'Specimen', order: 1 },
  { value: 'Register', order: 2 },
  { value: 'Label', order: 3 },
  { value: 'Document', order: 4 },
  { value: 'Other', order: 5 },
]);

function _makeFilterDict(arr, fieldNames, matchType = 'string_equals') {
  if (arr.length === 1) {
    let d = {};
    d[matchType] = {
      fields: fieldNames,
      value: arr[0],
    };
    return d;
  } else {
    return {
      or: arr.map((x) => {
        let d = {};
        d[matchType] = {
          fields: fieldNames,
          value: x,
        };
        return d;
      }),
    };
  }
}

function applyFilters() {
  let newQ = {
    query: {},
    resource_ids: [...store.query.resource_ids],
  };
  let newImageQ = {};
  if (modes.mode.enableFilters) {
    if (searchEverything.value) {
      newQ.query.search = searchEverything.value;
    }
    if (enableDwcFilters.value) {
      if (taxa.value || typeStatus.value || imageCategory.value) {
        // add filter group if any of the filters are present
        newQ.query.filters = { and: [] };
      }
      // now for the individual filters
      if (taxa.value) {
        newQ.query.filters.and.push(
          _makeFilterDict([taxa.value], taxaFields, 'string_contains'),
        );
      }
      if (typeStatus.value.length > 0) {
        newQ.query.filters.and.push(
          _makeFilterDict(typeStatus.value, ['typeStatus', 'materialType']),
        );
      }
      if (imageCategory.value.length > 0) {
        newQ.query.filters.and.push(
          _makeFilterDict(imageCategory.value, ['associatedMedia.category']),
        );
        newImageQ['category'] = imageCategory.value;
      }
    }
  }
  if (modes.mode.enableResources) {
    newQ.resource_ids = [...resources.value];
  }

  store.setQuery(newQ, newImageQ);
  model.value = false;
}

function parseQuery() {
  // NB this will only work for filters at the root, but this should only be shown for
  // simple queries anyway
  if (store.query.query) {
    searchEverything.value = store.query.query.search;

    if (store.query.query.filters && store.query.query.filters.and) {
      let _typeStatus = [];
      let _imageCategory = [];
      let _taxa = null;
      const _taxaFields = JSON.stringify(taxaFields.sort());

      function _parseGroup(g) {
        g.forEach((term) => {
          const termParts = Object.entries(term)[0];
          if (termParts[0] === 'or') {
            _parseGroup(termParts[1]);
          }
          if (termParts[0] !== 'string_equals') {
            return;
          }
          if (termParts[1].fields[0] === 'typeStatus') {
            _typeStatus.push(termParts[1].value);
          } else if (termParts[1].fields[0] === 'associatedMedia.category') {
            _imageCategory.push(termParts[1].value);
          } else if (
            JSON.stringify(termParts[1].fields.sort()) === _taxaFields
          ) {
            _taxa = termParts[1].value;
          }
        });
      }

      _parseGroup(store.query.query.filters.and);
      typeStatus.value = _typeStatus;
      imageCategory.value = _imageCategory;
      taxa.value = _taxa;
    }
  }
}

function clearAll() {
  searchEverything.value = null;
  taxa.value = null;
  typeStatus.value = [];
  imageCategory.value = [];
  if (modes.mode.enableResources) {
    resources.value = [];
  }
}

emitter.on(events.querySet, (newQuery) => {
  parseQuery();
});

onMounted(() => {
  resources.value = [...store.query.resource_ids];
  // wait for the multiselects to initialise or the values will be immediately
  // overwritten; this is probably a zoa bug
  setTimeout(parseQuery, 200);
});
</script>

<style module lang="scss">
.main {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1em;
  padding: 1em 1em 2em;
}

.input {
  & li label {
    white-space: nowrap;
    overflow-x: hidden;
    text-overflow: ellipsis;
  }

  & label {
    margin-bottom: 0;

    &::after {
      content: '';
    }
  }
}

.buttons {
  grid-column: span 1/-1;
  justify-self: end;
  align-self: end;
  display: flex;
  gap: 1em;
}
</style>

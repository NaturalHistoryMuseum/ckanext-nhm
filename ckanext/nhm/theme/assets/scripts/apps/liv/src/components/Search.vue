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
          :options="{ options: typeStatusOptions }"
          v-model="typeStatus"
          :class="$style.input"
        />
        <zoa-input
          zoa-type="multiselect"
          label="Image category"
          :options="{ options: imageCategoryOptions }"
          v-model="imageCategory"
          :class="$style.input"
        />
      </template>
    </template>
    <zoa-input
      zoa-type="multiselect"
      label="Resources"
      :options="{ options: resourceOptions }"
      v-model="resources"
      :class="$style.input"
      v-if="modes.mode && modes.mode.enableResources"
    />
    <zoa-button @click="applyFilters" :class="$style.apply">Apply</zoa-button>
  </div>
</template>

<script setup>
import { ZoaButton, ZoaInput } from '@nhm-data/zoa';
import { useModeStore, useStore } from '../store';
import { computed, onMounted, ref } from 'vue';

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
    ? resourceModels.value.every((r) => r.dwc)
    : false;
});

const taxa = ref(null);

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

function _makeFilterDict(arr, fieldName) {
  if (arr.length === 1) {
    return {
      string_equals: {
        fields: [fieldName],
        value: arr[0],
      },
    };
  } else {
    return {
      or: arr.map((x) => ({
        string_equals: {
          fields: [fieldName],
          value: x,
        },
      })),
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
        newQ.query.filters.and.push({
          string_equals: {
            fields: [
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
            ],
            value: taxa.value,
          },
        });
      }
      if (typeStatus.value.length > 0) {
        newQ.query.filters.and.push(
          _makeFilterDict(typeStatus.value, 'typeStatus'),
        );
      }
      if (imageCategory.value.length > 0) {
        newQ.query.filters.and.push(
          _makeFilterDict(imageCategory.value, 'associatedMedia.category'),
        );
        newImageQ['category'] = imageCategory.value;
      }
    }
  }
  if (modes.mode.enableResources) {
    newQ.resource_ids = [...resources.value];
  }

  store.setQuery(newQ, newImageQ);
}

onMounted(() => {
  resources.value = [...store.query.resource_ids];
  store.getAllResources();
});
</script>

<style module lang="scss">
.main {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1em;
  padding: 1em 1em 2em;
}

.input label {
  margin-bottom: 0;

  &::after {
    content: '';
  }
}

.apply {
  grid-column: span 1/-1;
  justify-self: end;
  align-self: end;
}
</style>

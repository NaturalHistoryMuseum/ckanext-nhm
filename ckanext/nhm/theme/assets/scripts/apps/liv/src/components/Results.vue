<template>
  <div>
    <div :class="$style.resultsHeader">
      <span :class="$style.status"
        >Loaded {{ store.allImages.length }} images from
        {{ store.totalRecords }} total records</span
      >
      <i class="fas fa-spinner fa-spin fa-lg" v-if="store.state.loading"></i>
    </div>
    <div :class="$style.buttons">
      <zoa-tabs
        :options="tabOptions"
        v-model="currentTab"
        :class="$style.viewTabs"
      />
      <zoa-button @click="resetAll" size="sm" :class="$style.resetButton">
        <i class="fas fa-undo-alt" />
        <span class="sr-only">Reset to defaults</span>
      </zoa-button>
      <zoa-toggle-button
        label="Filters"
        v-model="showFilters"
        :class="$style.filterButton"
        v-if="modes.mode && !modes.mode.lockAll"
      />
    </div>
    <KeepAlive>
      <Search v-if="showFilters" v-model="showFilters" />
    </KeepAlive>
    <template v-if="store.totalRecords > 0">
      <KeepAlive>
        <TabComponent />
      </KeepAlive>
    </template>
    <div
      v-else-if="store.state.attempted && !store.state.loading"
      :class="$style.noResults"
    >
      No results.
    </div>
  </div>
</template>

<script setup>
import {
  computed,
  defineAsyncComponent,
  onMounted,
  ref,
  shallowRef,
} from 'vue';
import { useStore, useModeStore } from '../store';
import { ZoaTabs, ZoaToggleButton, ZoaButton } from '@nhm-data/zoa';
import Search from './Search.vue';
import { useRouter } from 'vue-router';

const store = useStore();
const modes = useModeStore();
const router = useRouter();

// TABS
const tabs = shallowRef({
  gallery: defineAsyncComponent({
    loader: () => import('./views/Gallery.vue'),
  }),
  list: defineAsyncComponent({
    loader: () => import('./views/List.vue'),
  }),
});
const tabOptions = [
  { label: 'Gallery', value: 'gallery', order: 0 },
  { label: 'List', value: 'list', order: 1 },
];
const currentTab = ref(null);

const TabComponent = computed(() => {
  return tabs.value[currentTab.value];
});

// FILTERS
const showFilters = ref(false);

// MODES
function resetAll() {
  router.push('/').then(() => {
    window.location.reload();
  });
}

onMounted(() => {
  modes.loadData();
});
</script>

<style module lang="scss">
.resultsHeader {
  margin: 10px 0;
  padding: 5px 0;
  border-top: 1px solid black;
  border-bottom: 1px solid #9a9a9a;
  display: flex;
  align-items: center;
  gap: 10px;
}

.status {
  flex-grow: 1;
}

.viewTabs {
  padding-bottom: 5px;

  label::after {
    content: '';
  }
}

.buttons {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 5px;

  & > label::after {
    content: '';
  }
}

.resetButton {
  margin-bottom: 10px;
}

.filterButton {
  margin-bottom: 5px;
}

.noResults {
  text-align: center;
  padding: 3em;
  font-weight: bold;
}
</style>

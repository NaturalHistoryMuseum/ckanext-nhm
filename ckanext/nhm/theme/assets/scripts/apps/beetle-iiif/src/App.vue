<template>
  <div>
    <div class="secondary col-sm-3">
      <h1>Beetle Drawers</h1>
      <div class="biiif-page-description">
        Use the filters below to search by drawer code or collection. Please
        note that not all imaging has yet been completed, and this page will
        update over time.
      </div>
      <Filters />
    </div>
    <div class="col-sm-9 col-xs-12">
      <OpenSeadragonView width="100%" height="550px" />
      <RecordSelect />
    </div>
  </div>
</template>

<script>
import OpenSeadragonView from './components/OpenSeadragonView.vue';
import RecordSelect from './components/RecordSelect.vue';
import Filters from './components/Filters.vue';

export default {
  name: 'App',
  components: {
    Filters,
    OpenSeadragonView,
    RecordSelect,
  },
};
</script>

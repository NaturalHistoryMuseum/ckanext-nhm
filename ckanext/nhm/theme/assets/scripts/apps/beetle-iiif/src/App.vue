<template>
  <div>
    <div class="secondary col-sm-3">
      <Filters />
    </div>
    <div class="col-sm-9 col-xs-12">
      <OpenSeadragonView width="100%" height="550px" />
      <ThumbnailCarousel
        :fetch-size="15"
        :thumbnailSize="150"
        :fetchImmediately="false"
      />
    </div>
  </div>
</template>

<script>
import OpenSeadragonView from './components/OpenSeadragonView.vue';
import ThumbnailCarousel from './components/ThumbnailCarousel.vue';
import Filters from './components/Filters.vue';

export default {
  name: 'App',
  components: {
    Filters,
    OpenSeadragonView,
    ThumbnailCarousel,
  },
};
</script>

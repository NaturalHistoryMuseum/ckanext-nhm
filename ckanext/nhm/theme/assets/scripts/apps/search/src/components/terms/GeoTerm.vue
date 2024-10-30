<template>
  <div class="filter-term filter-term-geo">
    <span v-if="showName" class="filter-term-name">{{
      data.display.name
    }}</span>
    <div class="flex-container" v-if="!showName">
      <i class="fas" :class="icon"></i>
      <span v-if="comparison === 'point'"
        >({{ Math.round(data.content.latitude, 1) }} ,
        {{ Math.round(data.content.longitude, 1) }})</span
      >
      <span v-if="comparison === 'named_area'">{{ areaName }}</span>
      <span v-if="comparison === 'custom_area'"
        >{{ data.content.length }} polygon{{
          data.content.length !== 1 ? 's' : ''
        }}</span
      >
    </div>
  </div>
</template>

<script>
import BaseTerm from './BaseTerm.vue';

export default {
  extends: BaseTerm,
  name: 'GeoTerm',
  computed: {
    areaName() {
      return Object.values(this.data.content)[0];
    },
    icon() {
      if (this.comparison === 'point') {
        return 'fa-map-marker-alt';
      } else if (this.comparison === 'named_area') {
        return 'fa-globe-africa';
      } else {
        return 'fa-map';
      }
    },
  },
};
</script>

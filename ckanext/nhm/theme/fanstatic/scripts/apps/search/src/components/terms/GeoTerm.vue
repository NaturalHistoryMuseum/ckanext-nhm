<template>
    <div class="flex-container">
        <i class="fas" :class="icon"></i>
        <span v-if="comparison === 'point'">({{ Math.round(data.latitude,1) }} , {{ Math.round(data.longitude,1) }})</span>
        <span v-if="comparison === 'named_area'">{{ areaName }}</span>
        <span v-if="comparison === 'custom_area'">{{ data.length }} polygons</span>
    </div>
</template>

<script>
    import BaseTerm from './BaseTerm.vue';

    export default {
        extends: BaseTerm,
        name:    'GeoTerm',
        computed: {
            areaName() {
                return Object.values(this.data)[0];
            },
            icon() {
                if (this.comparison === 'point') {
                    return 'fa-map-marker-alt';
                }
                else if (this.comparison === 'named_area') {
                    return 'fa-globe-africa';
                }
                else {
                    return 'fa-map';
                }
            }
        }
    }
</script>
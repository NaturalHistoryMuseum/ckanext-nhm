<template>
  <div class="flex-container flex-column flex-center">
    <div class="flex-container flex-center" v-if="comparisonType === 'point'">
      <input
        type="text"
        title="Latitude"
        v-model="values.point.latitude"
        size="3"
        @keyup.enter="pressedEnter"
      />
      <span>,</span>
      <input
        type="text"
        title="Longitude"
        v-model="values.point.longitude"
        size="3"
        @keyup.enter="pressedEnter"
      />
      <label for="radius">±</label>
      <input
        type="number"
        title="Radius"
        v-model.number="values.point.radius"
        min="0"
        id="radius"
        @keyup.enter="pressedEnter"
      />
      <select v-model="values.point.radius_unit" title="Radius units">
        <option v-for="unit in radiusUnits" :key="unit.id">{{ unit }}</option>
      </select>
    </div>
    <div
      class="flex-container flex-center flex-column"
      v-if="comparisonType === 'named_area'"
    >
      <span>
        <label for="geoCategory">Category</label>
        <select v-model="geoCategory" id="geoCategory">
          <option v-for="(options, cat) in namedAreas" :key="cat.id">
            {{ cat }}
          </option>
        </select>
      </span>
      <span>
        <label for="geoName">Name</label>
        <select
          id="geoName"
          :disabled="!geoCategory"
          v-model="values.named_area[geoCategory]"
        >
          <option v-for="area in namedAreas[geoCategory] || []" :key="area.id">
            {{ area }}
          </option>
        </select>
      </span>
    </div>
    <div
      class="flex-container flex-center flex-column flex-stretch-height space-children-v full-width"
      v-if="comparisonType === 'custom_area'"
    >
      <div class="flex-container flex-wrap flex-wrap-spacing">
        <span
          class="fields"
          v-for="(polygon, index) in values.custom_area"
          v-bind:key="polygon.id"
        >
          {{ polygon.map((p) => p.length).reduce((a, b) => a + b, 0) }} points
          <i
            class="delete-field fas fa-times-circle fa-xs"
            @click="deletePolygon(index)"
          ></i>
        </span>
        <i
          class="fas fa-plus-square"
          @click="addPolygon"
          title="Add new polygon"
          role="button"
        ></i>
      </div>
      <div class="flex-container">
        <small>
          Click on the map to add polygon points. Try
          <a id="geojson-link" href="https://geojson.net">geojson.net</a> for
          editing more complex MultiPolygon queries.
        </small>
        <label for="useGeoJson">Paste GeoJSON</label>
        <input type="checkbox" v-model="useGeoJson" id="useGeoJson" />
      </div>
      <textarea
        v-model="pastedGeoJson"
        v-if="useGeoJson"
        placeholder="Paste a list of MultiPolygon coordinates, e.g. [[[[1, 1], [0, 0], [1, 0], [1, 1]]]]"
      >
      </textarea>
      <button @click="parseGeoJson" class="btn btn-primary">Set</button>
    </div>
    <div id="mapdisplay" v-if="comparisonType !== 'named_area'"></div>
  </div>
</template>

<script>
import BaseEditor from './BaseEditor.vue';
import L from 'leaflet';
import { mapState } from 'vuex';
import * as d3 from 'd3-collection';

export default {
  extends: BaseEditor,
  name: 'GeoEditor',
  data: function () {
    return {
      values: {
        point: {
          latitude: null,
          longitude: null,
          radius: 0,
          radius_unit: 'mi',
        },
        named_area: {
          country: null,
          marine: null,
          geography: null,
        },
        custom_area: [[]],
      },
      geoCategory: null,
      leafletMap: null,
      markers: {
        point: {
          group: L.layerGroup(),
          circle: L.circle(),
          marker: L.marker(),
        },
        named_area: {
          group: L.layerGroup(),
          data: null,
        },
        custom_area: {
          group: L.layerGroup(),
        },
      },
      pastedGeoJson: null,
      currentPolygon: [],
      useGeoJson: false,
      mapInitialised: false,
    };
  },
  computed: {
    ...mapState(['schema']),
    radiusUnits() {
      return this.schema.raw.definitions.term.properties.geo_point.properties
        .radius_unit.enum;
    },
    namedAreas() {
      return d3
        .nest()
        .key((d) => d.key)
        .rollup((d) => d[0].value.enum)
        .object(
          d3.entries(
            this.schema.raw.definitions.term.properties.geo_named_area
              .properties,
          ),
        );
    },
    radiusMeters() {
      let conversions = {
        mi: (x) => x / 0.00062137,
        yd: (x) => x / 1.0936,
        ft: (x) => x / 3.2808,
        in: (x) => x / 39.37,
        km: (x) => x * 1000,
        m: (x) => x,
        cm: (x) => x / 100,
        mm: (x) => x / 1000,
        nmi: (x) => x / 0.00053996,
      };
      return conversions[this.values.point.radius_unit](
        this.values.point.radius,
      );
    },
  },
  methods: {
    loadExisting() {
      if (this.existingTermId === undefined) {
        return;
      }
      let existing = this.getFilterById(this.existingTermId);

      if (this.comparisonType !== 'custom_area') {
        d3.keys(this.values[this.comparisonType]).forEach((k) => {
          this.$set(
            this.values[this.comparisonType],
            k,
            existing.content[k] || null,
          );
        });
      } else {
        this.$set(this.values, 'custom_area', existing.content);
      }

      if (this.comparisonType === 'named_area') {
        this.geoCategory = d3.keys(existing.content).filter((k) => {
          return d3.keys(this.namedAreas).includes(k);
        })[0];
      }
    },
    setLatLng(event) {
      if (this.comparisonType === 'point') {
        this.$set(this.values.point, 'latitude', event.latlng.lat);
        this.$set(this.values.point, 'longitude', event.latlng.lng);
      }
      if (this.comparisonType === 'custom_area') {
        if (this.useGeoJson) {
          return;
        }
        let lnglat = [event.latlng.lng, event.latlng.lat];

        if (this.currentPolygon.length === 0) {
          // insert the first coordinates at the beginning and end of the polygon
          // to make a loop
          this.currentPolygon.push(lnglat);
          this.currentPolygon.push(lnglat);
        } else {
          // insert at the penultimate position
          this.currentPolygon.splice(this.currentPolygon.length - 1, 0, lnglat);
        }
        this.$set(this.values.custom_area, this.values.custom_area.length - 1, [
          this.currentPolygon,
        ]);
      }
    },
    resetMap() {
      d3.values(this.markers).forEach((x) => {
        if (this.leafletMap.hasLayer(x.group)) {
          this.leafletMap.removeLayer(x.group);
        }
      });
      this.markers[this.comparisonType].group.addTo(this.leafletMap);

      this.leafletMap.on('click', this.setLatLng);
    },
    parseGeoJson() {
      if (this.pastedGeoJson === null) {
        return;
      }
      let coords = [];
      let cont = true;
      try {
        coords = JSON.parse(this.pastedGeoJson);
      } catch (e) {
        cont = false;
        console.log('Invalid JSON.');
      }
      if (cont) {
        this.$set(this.values, 'custom_area', coords);
      }
    },
    setGeoJson() {
      this.markers.custom_area.group.clearLayers();
      try {
        let geoj = {
          type: 'MultiPolygon',
          coordinates: this.values.custom_area,
        };
        this.markers.custom_area.group.addLayer(L.geoJSON(geoj));
      } catch (e) {
        console.log(e);
        this.markers.custom_area.group.addLayer(
          L.popup()
            .setLatLng(this.leafletMap.getCenter())
            .setContent('Invalid GeoJSON.'),
        );
      }
    },
    addPolygon() {
      this.pastedGeoJson = null;
      this.currentPolygon = [];
      this.values.custom_area.push([]);
    },
    deletePolygon(index) {
      this.$delete(this.values.custom_area, index);
    },
    initMap() {
      this.leafletMap = L.map('mapdisplay');
      this.leafletMap.setView([0, 0], 0);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
      }).addTo(this.leafletMap);
      this.resetMap();
      this.mapInitialised = true;
    },
  },
  mounted() {
    if (this.comparisonType !== 'named_area') {
      this.initMap();
    }
  },
  watch: {
    comparisonType() {
      if (this.comparisonType === 'named_area') {
        return;
      }
      if (this.mapInitialised) {
        this.resetMap();
      } else {
        // give time for the DOM to load
        setTimeout(this.initMap, 1000);
      }
    },
    'values.point': {
      handler: function () {
        let latLng = [this.values.point.latitude, this.values.point.longitude];

        if (latLng.some((x) => x === null || x === '')) {
          this.markers.point.group.clearLayers();
          return;
        }

        this.leafletMap.setView(latLng);

        this.markers.point.marker.setLatLng(latLng);
        if (!this.markers.point.group.hasLayer(this.markers.point.marker)) {
          this.markers.point.group.addLayer(this.markers.point.marker);
        }

        if (this.values.point.radius > 0) {
          this.markers.point.circle.setLatLng(latLng);
          this.markers.point.circle.setRadius(this.radiusMeters);

          if (!this.markers.point.group.hasLayer(this.markers.point.circle)) {
            this.markers.point.group.addLayer(this.markers.point.circle);
          }
        } else {
          this.markers.point.group.removeLayer(this.markers.point.circle);
        }
      },
      deep: true,
    },
    'values.named_area': {
      handler: function (namedArea) {
        let entries = d3.entries(namedArea);
        if (
          entries
            .map((e) => (e.value !== null ? 1 : 0))
            .reduce((a, b) => a + b) > 1
        ) {
          entries.forEach((e) => {
            this.$set(this.values.named_area, e.key, null);
          });
        }
      },
      deep: true,
    },
    'values.custom_area': {
      handler: function () {
        this.pastedGeoJson = JSON.stringify(this.values.custom_area);
        this.setGeoJson();
      },
      deep: true,
    },
  },
};
</script>

<style scoped>
input,
select {
  margin: 2px;
}

#radius {
  width: 45px;
}

#mapdisplay {
  height: 200px;
  width: 100%;
  margin-top: 5px;
}

small {
  text-align: left;
  padding-right: 10px;
}
</style>

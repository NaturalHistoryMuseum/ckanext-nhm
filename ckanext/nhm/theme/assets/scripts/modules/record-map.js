/**
 * Record map module.
 * This is essentially a copy of the ckanext-spatial's dataset-map module. This has been copied into
 * here because ckanext-spatial hasn't been upgraded to Python3 support yet and therefore we can't
 * use it yet. We've tidied the module up a bit and streamlined it to our specific needs given that
 * it's now in our ckanext-nhm repo and no one else is going to be using it, this is most noticeable
 * in the fact we've removed the options that come from the ckan config and just hard coded the
 * settings we want to use.
 */
this.ckan.module('record-map', function () {
  return {
    initialize: function () {
      const extent = this.el.data('extent');

      if (!!extent) {
        const map = new L.Map('record-map-container');

        // create the base tile layer
        const baseLayerUrl =
          'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
        const baseLayer = new L.TileLayer(baseLayerUrl, {
          maxZoom: 18,
          subdomains: 'abc',
        });
        map.addLayer(baseLayer);

        // setup the icon point we want to use to show the location of the specimen
        const pointOptions = {
          iconUrl: '/images/leaflet/marker-icon-2x.png',
          iconSize: [28, 50],
          iconAnchor: [14, 50],
        };
        const ckanIcon = L.Icon.extend({ options: pointOptions });

        // create the layer that shows the point and add it to the map
        const extentLayer = L.geoJson(extent, {
          pointToLayer: function (feature, latLng) {
            return new L.Marker(latLng, { icon: new ckanIcon() });
          },
        });
        extentLayer.addTo(map);

        // ensure we get a nice view of the marker
        map.setView(L.latLng(extent.coordinates[1], extent.coordinates[0]), 9);
      }
    },
  };
});

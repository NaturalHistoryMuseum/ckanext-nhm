<template>
  <div>
    <h2>{{ viewerTitle }}</h2>
    <div :id="viewerId" :style="viewerStyle"></div>
  </div>
</template>

<script>
import OpenSeadragon from 'openseadragon';
import axios from 'axios';
import { mapState } from 'vuex';

export default {
  name: 'OpenSeadragonView',
  props: {
    viewerId: {
      default: 'osd_viewer',
    },
    width: {
      default: '100%',
    },
    height: {
      default: '550px',
    },
  },
  data() {
    return {
      viewer: null,
    };
  },
  computed: {
    ...mapState(['record']),
    viewerStyle() {
      return {
        width: this.width,
        height: this.height,
      };
    },
    viewerTitle() {
      try {
        const record = this.record.data;
        return `${record['Collection Name']}: ${record['Barcode']}`;
      } catch {
        return '';
      }
    },
  },
  watch: {
    /**
     * Watch when the store state's record changes and update the viewer accordingly. This
     * function attempts to load the image using IIIF by requesting its info.json and
     * passing the resulting JSON to the viewer. If this fails, we just pass the image URL
     * to the viewer directly assuming it's not a IIIF image.
     *
     * @param newRecord the new record
     */
    '$store.state.record': async function (newRecord) {
      if (newRecord != null) {
        // TODO: deal with more than just the first image in the manifest
        const image_url = newRecord.iiif.items[0].items[0].items[0].body.id;
        try {
          const info_json = await axios.get(`${image_url}/info.json`);
          this.viewer.open(info_json.data);
        } catch (e) {
          this.viewer.open({ type: 'image', url: image_url });
        }
      } else {
        this.viewer.close();
      }
    },
  },
  mounted() {
    // init the OpenSeadragon viewer
    this.viewer = OpenSeadragon({
      id: 'osd_viewer',
      // TODO: need to change this to use the images in the node module
      prefixUrl:
        'https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/images/',
      sequenceMode: false,
      showRotationControl: true,
      tileSources: [],
    });
  },
};
</script>

<template>
    <div>
        <div :id="viewerId" :style="viewerStyle"></div>
    </div>
</template>

<script>
    import OpenSeadragon from 'openseadragon';

    export default {
        name: "OpenSeadragonView",
        props: {
            currentRecord: {
                type: Object
            },
            viewerId: {
                default: 'osd_viewer'
            },
            width: {
                default: '100%'
            },
            height: {
                default: '550px'
            }
        },
        data() {
            return {
                viewer: null,
                annotations: null
            }
        },
        computed: {
            viewerStyle() {
                return {
                    width: this.width,
                    height: this.height
                }
            },
        },
        watch: {
            currentRecord(newRecord) {
                if (newRecord != null) {
                    this.viewer.open(`/iiif_images/${newRecord['Image']}/info.json`);
                } else {
                    this.viewer.close();
                }
            }
        },
        mounted() {
            this.viewer = OpenSeadragon({
                id: "osd_viewer",
                // need to change this to use the images in the node module
                prefixUrl: "https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/images/",
                sequenceMode: false,
                tileSources: []
            });
        }
    }
</script>

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
                viewer: null
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
            /**
             * Watch when the store state's record changes and update the viewer accordingly.
             *
             * @param newRecord the new record
             */
            '$store.state.record': function(newRecord) {
                if (newRecord != null) {
                    // only deal with the first image in the manifest
                    this.viewer.open(newRecord.iiif.items[0].items[0].items[0].body.id);
                } else {
                    this.viewer.close();
                }
            }
        },
        mounted() {
            // init the OpenSeadragon viewer
            this.viewer = OpenSeadragon({
                id: "osd_viewer",
                // TODO: need to change this to use the images in the node module
                prefixUrl: "https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/images/",
                sequenceMode: false,
                tileSources: []
            });
        }
    }
</script>

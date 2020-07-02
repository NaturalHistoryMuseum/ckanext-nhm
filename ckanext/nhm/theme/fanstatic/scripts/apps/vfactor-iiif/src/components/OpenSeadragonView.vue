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
            resourceId: {
                type: String,
                required: true
            },
            manifests: {
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
            }
        },
        watch: {
            currentRecord(newRecord) {
                if (newRecord != null && !!this.manifests[newRecord._id]) {
                    const iiifManifest = this.manifests[newRecord._id];
                    // only deal with the first image in the manifest
                    this.viewer.open(iiifManifest.items[0].items[0].items[0].body.id);
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

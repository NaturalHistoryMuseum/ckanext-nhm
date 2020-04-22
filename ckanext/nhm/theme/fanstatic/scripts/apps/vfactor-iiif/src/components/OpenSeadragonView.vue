<template>
    <div>
        <div :id="viewerId" class="viiif-osd-viewer" :style="viewerStyle">
            <a class="viiif-osd-manifest-link" v-if="currentRecord !== null" target="_blank"
               :href="`/iiif/resource/${this.resourceId}/record/${this.currentRecord._id}`">
                View IIIF Manifest <i class="fas fa-link inline-icon-right"></i>
            </a>
        </div>
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
                if (newRecord != null) {
                    this.viewer.open(`/iiif_images/vfactor:${newRecord['Image']}/info.json`);
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

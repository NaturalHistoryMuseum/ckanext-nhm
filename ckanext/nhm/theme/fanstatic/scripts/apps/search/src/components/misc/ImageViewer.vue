<template>
    <div class="image-viewer" @click.self="hideImage">
        <div class="scrolling-arrows">
            <div class="scroll-left" @click="setViewerImage(viewerImageIndex - 1)" v-if="!firstImage">
                <i class="fas fa-angle-double-left"></i>
            </div>
            <div class="scroll-right" @click="setViewerImage(viewerImageIndex + 1)" v-if="!lastImage">
                <i class="fas fa-angle-double-right"></i>
            </div>
        </div>
        <img :src="viewerImage.image.preview" :alt="viewerImage.image.title">
        <h4><a :href="viewerImage.recordUrl">{{ viewerImage.image.title }}</a></h4>
    </div>
</template>

<script>
    import { mapState, mapMutations, mapGetters } from 'vuex';

    export default {
        name: 'ImageViewer',
        computed: {
            ...mapState('results/display', ['viewerImageIndex', 'viewerImagePage']),
            ...mapGetters('results/display', ['viewerImage']),
            firstImage() {
                return this.viewerImageIndex === 0;
            },
            lastImage() {
                return this.viewerImagePage.length < (this.viewerImageIndex + 1);
            }
        },
        methods: {
            ...mapMutations('results/display', ['hideImage', 'setViewerImage'])
        }
    }
</script>
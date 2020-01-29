<template>
    <div class="image-viewer" @click.self="hideImage">
        <h4><a :href="viewerImage.recordUrl">{{ viewerImage.image.title }}</a></h4>
        <div class="scrolling-arrows">
            <div class="scroll-left" @click="previousImage" v-if="!firstImage">
                <i class="fas fa-angle-double-left"></i>
            </div>
            <div class="scroll-right" @click="nextImage" v-if="!lastImage">
                <i class="fas fa-angle-double-right"></i>
            </div>
        </div>
        <img :src="viewerImage.image.preview" :alt="viewerImage.image.title">
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
            ...mapMutations('results/display', ['hideImage', 'setViewerImage']),
            previousImage() {
                if (!this.firstImage) {
                    this.setViewerImage(this.viewerImageIndex - 1);
                }
            },
            nextImage() {
                if (!this.lastImage) {
                    this.setViewerImage(this.viewerImageIndex + 1);
                }
            },
            keyListener(event) {
                if (event.key === 'ArrowRight') {
                    this.nextImage();
                }
                else if (event.key === 'ArrowLeft') {
                    this.previousImage();
                }
                else if (event.key === 'Escape') {
                    this.hideImage()
                }
            }
        },
        mounted() {
            $(document).on('keyup', this.keyListener);
        },
        beforeDestroy() {
            $(document).off('keyup', this.keyListener);
        }
    }
</script>
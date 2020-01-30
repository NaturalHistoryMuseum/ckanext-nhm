<template>
    <div class="image-viewer" @click.self="hideImage">
        <div class="flex-container flex-stretch-first image-viewer-header">
            <h4><a :href="viewerImage.recordUrl">{{ viewerImage.image.title }}</a></h4>
            <span class="image-viewer-icon"><i class="fas fa-download"></i></span>
            <span class="image-viewer-icon" @click="hideImage"><i class="fas fa-times"></i></span>
        </div>
        <div class="scrolling-arrows">
            <div class="scroll-left" @click="previousImage" v-if="!firstImage">
                <i class="fas fa-angle-double-left"></i>
            </div>
            <div class="scroll-right" @click="nextImage" v-if="!lastImage">
                <i class="fas fa-angle-double-right"></i>
            </div>
        </div>
        <img v-images-loaded:on.done="loadImage"
             :src="viewerImage.image.preview"
             :alt="viewerImage.image.title"
             class="main-image" :class="{loading: loading}">
        <Loading v-if="loading"></Loading>

    </div>
</template>

<script>
    import {mapGetters, mapMutations, mapState} from 'vuex';
    import imagesLoaded from 'vue-images-loaded';
    import Loading from '../Loading.vue';
    import LoadError from '../LoadError.vue';

    export default {
        name:       'ImageViewer',
        data:       function () {
            return {
                loading:   true,
                loadError: false
            }
        },
        directives: {
            imagesLoaded
        },
        components: {
            Loading,
            LoadError
        },
        computed:   {
            ...mapState('results/display', ['viewerImageIndex', 'viewerImagePage']),
            ...mapGetters('results/display', ['viewerImage']),
            firstImage() {
                return this.viewerImageIndex === 0;
            },
            lastImage() {
                return this.viewerImagePage.length < (this.viewerImageIndex + 1);
            }
        },
        methods:    {
            ...mapMutations('results/display', ['hideImage', 'setViewerImage']),
            previousImage() {
                if (!this.firstImage) {
                    this.loading = true;
                    this.setViewerImage(this.viewerImageIndex - 1);
                }
            },
            nextImage() {
                if (!this.lastImage) {
                    this.loading = true;
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
            },
            loadImage(instance) {
                this.loading   = false;
                this.loadError = instance.hasAnyBroken;
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
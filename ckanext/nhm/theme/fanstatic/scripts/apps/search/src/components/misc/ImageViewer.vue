<template>
    <div class="image-viewer" @click.self="hideImage">
        <div class="flex-container flex-stretch-first image-viewer-header">
            <h4><a :href="viewerImage.recordUrl">{{ viewerImage.image.title }}</a></h4>
            <div class="info-popup-button" v-if="isMAM">
                <transition name="slidedown">
                    <div class="floating info-popup download-popup"
                         v-if="showDownload"
                         v-dismiss="{switch: 'showDownload', ignore: ['#show-download']}">
                        <p v-if="download !== null">
                            Success! You should receive an email at <b>{{ email }}</b> soon.</p>
                        <p class="alert-error" v-if="downloadStatus.failed">
                            The download request failed. Please try again later.</p>
                        <div v-if="download === null">
                            <p>Please enter your email address, and we will send you the original
                               image.</p>
                            <div class="form-row">
                                <label for="download-email" class="control-label">
                                    <span class="control-required">*</span>Your email</label> <input
                                id="download-email"
                                type="text"
                                class="full-width"
                                v-model="email"
                                placeholder="data@nhm.ac.uk">
                            </div>
                        </div>
                        <div class="privacy-warning">
                            <p><i>Data Protection</i></p>
                            <p>The Natural History Museum will use your personal data in accordance
                               with data protection legislation to process your requests. For more
                               information please read our <a href="/privacy">privacy notice</a>.
                            </p>
                        </div>
                        <div class="text-right" v-if="download === null">
                            <a href="#"
                               class="btn btn-primary text-right"
                               @click="downloadMAMImage"> <i class="fas"
                                                             :class="downloadStatus.loading ? ['fa-pulse', 'fa-spinner'] : ['fa-download']"></i>
                                Request Download </a>
                        </div>
                    </div>
                </transition>
                <span class="image-viewer-icon"
                      @click="showDownload = !showDownload"
                      id="show-download">
                    <i class="fas fa-cloud-download-alt fa-2x"></i>
                </span>
            </div>
            <a class="image-viewer-icon" v-if="!isMAM" :href="viewerImage.image.preview" download><i
                class="fas fa-cloud-download-alt fa-2x"></i></a> <span class="image-viewer-icon"
                                                                       @click="hideImage"><i class="fas fa-times fa-2x"></i></span>
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
    import {post} from '../../store/utils';

    export default {
        name:       'ImageViewer',
        data:       function () {
            return {
                loading:        true,
                loadError:      false,
                email:          null,
                showDownload:   false,
                download:       null,
                downloadStatus: {
                    failed:  false,
                    loading: false
                }
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
            },
            isMAM() {
                return this.viewerImage.image.preview.startsWith('https://www.nhm.ac.uk/services/media-store/asset/')
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
            },
            downloadMAMImage() {
                let body = {
                    'resource_id': this.viewerImage.record.resource,
                    'record_id':   this.viewerImage.record.data._id,
                    'asset_id':    this.viewerImage.image.id,
                    'email':       this.email
                };

                this.downloadStatus.loading = true;
                this.downloadStatus.failed  = false;
                post('download_image', body)
                    .then(data => {
                        if (data.success) {
                            this.download = data;
                        }
                        else {
                            throw Error;
                        }
                    })
                    .catch(error => {
                        this.downloadStatus.failed = true;
                    })
                    .finally(() => {
                        this.downloadStatus.loading = false;
                    })
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
<template>
    <div class="view-component">
        <Loading v-if="loading && imageRecords.length > 0"><h3>Loading {{ nLoaded }} of {{
                                                               imageRecords.length }} images...</h3>
        </Loading>
        <LoadError v-if="loadError"></LoadError>
        <h4 v-if="!loading">{{ imageRecords.length }} images</h4>
        <div class="tiling-gallery full-width"
             v-images-loaded:on.progress="loadImages"
             :class="{'processing': loading || loadError}">
            <div class="gallery-column-sizer"></div>
            <div v-for="(record, recordIndex) in imageRecords"
                 :key="record.id"
                 class="gallery-tile">
                <img @click="setViewerImage(recordIndex)"
                     :src="record.image.thumb"
                     :alt="record.image.preview"> <small class="gallery-tile-title">
                <a :href="record.recordUrl">{{ record.recordTitle }}</a> </small>
                <small class="gallery-tile-number">{{ record.recordImageIndex + 1 }} / {{
                                                   record.imageTotal }}</small>
            </div>
        </div>

    </div>
</template>

<script>
    import BaseView from './BaseView.vue';
    import imagesLoaded from 'vue-images-loaded';
    import Loading from '../Loading.vue';
    import LoadError from '../LoadError.vue';

    import {mapActions, mapGetters, mapMutations} from 'vuex';

    export default {
        extends:    BaseView,
        name:       'GalleryView',
        data:       function () {
            return {
                loading:        true,
                loadError:      false,
                nLoaded:        0,
                loadTimeout:    false,
                presetData:     {
                    key:    'hasImage',
                    parent: 'group_root',
                    display: {
                        hidden: true,
                        temp: true
                    }
                }
            }
        },
        components: {
            Loading,
            LoadError
        },
        directives: {
            imagesLoaded
        },
        computed:   {
            ...mapGetters('results/query/filters', ['hasFilter']),
            imageRecords() {
                let imgRecords = [];

                this.records.forEach((r, rix) => {
                    let resourceDetails = this.getDetails(r.resource);
                    let recordUrl       = `${resourceDetails.resourceUrl}/record/${r.data._id}`;
                    let recordTitle     = r.data[resourceDetails.titleField] || r.data._id;
                    this.getImages(r, false).forEach((i, iix, ia) => {
                        imgRecords.push({
                                            record:           r,
                                            image:            i,
                                            recordImageIndex: iix,
                                            recordIndex:      rix,
                                            imageTotal:       ia.length,
                                            recordUrl,
                                            recordTitle
                                        })
                    })
                });

                return imgRecords;
            },
        },
        methods:    {
            ...mapMutations('results/display', ['setViewerImage', 'addPageImages']),
            ...mapActions('results', ['runSearch']),
            ...mapActions('results/query/filters', ['addPreset']),
            relayout(loadFinished) {
                this.loading = loadFinished;
                $('.tiling-gallery').masonry({
                                                 itemSelector:    '.gallery-tile',
                                                 columnWidth:     '.gallery-column-sizer',
                                                 percentPosition: true
                                             })
            },
            loadFailed() {
                this.loading   = false;
                this.loadError = true;
            },
            loadImages(instance) {
                this.nLoaded = instance.progressedCount;
                if (instance.isComplete || (this.loadTimeout && instance.progressedCount > Math.floor(instance.images.length * 0.1))) {
                    this.relayout(!instance.isComplete);
                }
            },
        },
        created() {
            this.addPreset(this.presetData).then(wasAdded => {
                if (wasAdded) {
                    this.runSearch(0);
                }
            });
            this.addPageImages(this.imageRecords);
            setTimeout(() => {
                this.loadTimeout = true;
            }, 1000)
        }
    }
</script>
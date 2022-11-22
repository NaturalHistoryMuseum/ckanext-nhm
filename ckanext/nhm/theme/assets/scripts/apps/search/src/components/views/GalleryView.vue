<template>
    <div class="view-component">
        <LoadError v-if="loadError"></LoadError>
        <div class="flex-container flex-right">
            <small v-if="!loading">{{ imageRecords.length }} images associated with {{ recordTag }}s {{ (page * 100) + 1 }} - {{ (page * 100) + records.length }}</small>
        </div>
        <div class="tiling-gallery full-width"
             v-images-loaded:on.progress="loadImages"
             :class="{'processing': loading || loadError}">
            <div class="gallery-column-sizer"></div>
            <div v-for="(record, recordIndex) in loadedImageRecords"
                 :key="record.id"
                 class="gallery-tile">
                <img @click="setViewerImage(recordIndex)" :src="record.image.thumb"
                     :alt="`Image associated with record ${record.id}`" >
                <small class="gallery-tile-title">
                    <a :href="record.recordUrl" :aria-label="`Go to record ${record.id}`">
                        {{ record.recordTitle }}
                    </a>
                </small>
                <small class="gallery-tile-number">
                    {{ record.recordImageIndex + 1 }} / {{record.imageTotal }}
                </small>
            </div>
        </div>
        <div class="flex-container flex-column flex-center pad-v space-children-v" v-if="brokenImageRecords.length > 0">
            <p>{{ brokenImageRecords.length }} thumbnail{{brokenImageRecords.length > 1 ? 's' : ''}} could not be loaded.</p>
            <small>View <i class="fas" :class="showBroken ? 'fa-caret-square-up' : 'fa-caret-square-down'" @click="showBroken = !showBroken"></i></small>
        </div>
        <div class="full-width flex-container flex-wrap flex-between tiling-gallery" v-if="showBroken">
            <div v-for="(record, recordIndex) in brokenImageRecords"
                 :key="record.id" class="gallery-tile gallery-tile-tiny">
                <img :src="record.image.thumb" :alt="record.image.preview"> <small class="gallery-tile-title">
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

    import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';

    export default {
        extends:    BaseView,
        name:       'GalleryView',
        data:       function () {
            return {
                loading:     true,
                loadError:   false,
                nLoaded:     0,
                loadTimeout: false,
                presetData:  {
                    key:     'hasImage',
                    parent:  'group_root',
                    display: {
                        hidden: true,
                        temp:   true
                    }
                },
                showBroken: false
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
            ...mapState('results/display', ['recordTag']),
            ...mapGetters('results/query/filters', ['hasFilter']),
            brokenImageRecords() {
                return this.imageRecords.filter(r => r.image.isBroken).map(r => {
                    if (r.record.data.collectionCode !== undefined) {
                        let collectionCode = r.record.data.collectionCode === 'BMNH(E)' ? 'ent' : r.record.data.collectionCode.toLowerCase();
                        r.image.thumb = '/images/icons/' + collectionCode + '.svg';
                    }
                    return r;
                })
            }
        },
        methods:    {
            ...mapMutations('results/display', ['setFilteredRecordTag']),
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
            this.setFilteredRecordTag(this.recordTag + '$ with images');
            this.addPageImages(this.loadedImageRecords);
            setTimeout(() => {
                this.loadTimeout = true;
            }, 1000)

            this.loading = this.loadedImageRecords.length > 0;
        }
    }
</script>

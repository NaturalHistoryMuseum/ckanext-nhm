<template>
    <div style="margin-top: 15px;">
        <Loading v-if="loading"><h3>Loading {{ imageRecords.length }} images...</h3></Loading>
        <LoadError v-if="loadError"></LoadError>
        <div class="tiling-gallery full-width"
             v-images-loaded:on.done="loadFinished"
             v-images-loaded:on.fail="loadFailed"
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

    import {mapActions, mapMutations} from 'vuex';

    export default {
        extends:    BaseView,
        name:       'GalleryView',
        data:       function () {
            return {
                loading:   true,
                loadError: false
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
            imageRecords() {
                let imgRecords = [];

                this.records.forEach((r, rix, ra) => {
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
            }
        },
        methods:    {
            ...mapMutations('results/display', ['setViewerImage', 'addPageImages']),
            ...mapActions('results', ['runSearch']),
            ...mapActions('results/query/filters', ['addPreset']),
            loadFinished() {
                this.loading = false;
                $('.tiling-gallery').masonry({
                                                 itemSelector:    '.gallery-tile',
                                                 columnWidth:     '.gallery-column-sizer',
                                                 percentPosition: true
                                             })
            },
            loadFailed() {
                this.loading   = false;
                this.loadError = true;
            }
        },
        created() {
            this.addPreset({key: 'hasImage', parent: 'group_root'}).then(wasAdded => {
                if (wasAdded) {
                    this.runSearch(0)
                }
            });
            this.addPageImages(this.imageRecords);

            // let loader = imagesLoaded('.tiling-gallery .gallery-tile');
            // loader.on('always', () => {
            //     console.log(loader.images.length);
            // });
        }
    }
</script>
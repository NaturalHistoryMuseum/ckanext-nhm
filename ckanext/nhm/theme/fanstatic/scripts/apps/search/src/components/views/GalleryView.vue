<template>
    <div class="tiling-gallery full-width" style="margin-top: 15px;">
        <template v-for="item in records">
            <div v-for="(image, index) in getImages(item, false)"
                 :key="image.id"
                 class="gallery-tile">
                <img @click="setImage(image)" :src="image.thumb" :alt="image.preview">
                <small class="gallery-tile-title">
                    <a :href="`${getDetails(item.resource).resourceUrl}/record/${item.data._id}`">
                        {{ item.data[getDetails(item.resource).titleField] || item.data._id }} </a>
                </small>
            </div>
        </template>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';

    import {mapGetters, mapMutations, mapActions} from 'vuex';

    export default {
        extends:    BaseView,
        name:       'GalleryView',
        methods:    {
            ...mapMutations('results/display', ['setImage']),
            ...mapActions('results', ['runSearch']),
            ...mapActions('results/query/filters', ['addPreset'])
        },
        created() {
            this.addPreset({key: 'hasImage', parent: 'group_root'}).then(wasAdded => {
                if (wasAdded) {
                    this.runSearch(0)
                }
            });
        }
    }
</script>
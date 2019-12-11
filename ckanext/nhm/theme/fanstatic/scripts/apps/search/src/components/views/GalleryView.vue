<template>
    <div class="tiling-gallery full-width" style="margin-top: 15px;">
        <template v-for="item in records">
            <div v-for="(image, index) in getImages(item, false)" :key="image.id" class="gallery-tile">
                <a :href="image.preview">
                    <img :src="image.thumb" :alt="image.preview"> </a>
                <small class="gallery-tile-title">
                    <a :href="`${getDetails(item.resource).resourceUrl}/record/${item.data._id}`">
                        {{ item.data[getDetails(item.resource).titleField] || item.data._id }}
                        </a>
                </small>
            </div>
        </template>
    </div>
</template>

<script>
    import BaseView from './BaseView.vue';

    export default {
        extends: BaseView,
        name:    'GalleryView',
        data:    function () {
            return {
                showDetails: null
            }
        },
        created() {
            this.$store.dispatch('setHasImage');
        }
    }
</script>
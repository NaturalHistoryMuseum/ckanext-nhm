<template>
    <div class="image-viewer" @click.self="hideImage">
        <img :src="viewerImage.preview" :alt="viewerImage.preview">
        <h4>{{ viewerImage.title }}</h4>
    </div>
</template>

<script>
    import { mapState, mapMutations } from 'vuex';

    export default {
        name: 'ImageViewer',
        computed: {
            ...mapState('results/display', ['viewerImage'])
        },
        methods: {
            ...mapMutations('results/display', ['hideImage'])
        }
    }
</script>
<template>
    <div id="result">
        <div class="flex-container flex-left flex-stretch-first">
            <h3>{{ total }} records</h3>
            <div style="position: relative;">
                <transition name="slidedown">
                    <div class="floating info-popup" v-if="showCite">
                        {{ doi }}
                    </div>
                </transition>
                <a href="#" @click="citeSearch" class="btn btn-disabled">
                    <i class="fas fa-book"></i>Cite
                </a>
            </div>
            <div style="position: relative;">
                <transition name="slidedown">
                    <div class="floating info-popup" v-if="showShare">
                        <a :href="`/search/${slug}`">{{ slug }}</a>
                    </div>
                </transition>
                <a href="#" @click="shareSearch" class="btn btn-disabled">
                    <i class="fas fa-share-alt"></i>Share
                </a>
            </div>
            <div style="position: relative;">
                <transition name="slidedown">
                    <div class="floating info-popup" v-if="showDownload">
                        Coming soon!
                    </div>
                </transition>
                <a href="#" v-if="total > 0" @click="downloadResults" class="btn btn-disabled">
                    <i class="fas fa-cloud-download-alt"></i>Download
                </a>
            </div>
        </div>
        <component :is="viewType"></component>
        <div class="pagination-wrapper" v-if="after.length > 0">
            <ul class="pagination">
                <li v-if="page > 0">
                    <a href="#" @click="runSearch(page - 1)">{{ page }}</a>
                </li>
                <li class="active">
                    <a href="#">{{ page + 1 }}</a>
                </li>
                <li>
                    <a href="#" @click="runSearch(page + 1)">{{ page + 2}}</a>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
    import TableView from './views/TableView.vue';
    import {mapActions, mapState, mapGetters} from 'vuex'

    export default {
        name:       'Results',
        components: {
            TableView
        },
        data:     function () {
            return {
                showDownload:    false,
                showCite: false,
                showShare: false,
                viewType: TableView,
                doi: ''
            }
        },
        computed: {
            ...mapState('results', ['page', 'after', 'current', 'slug']),
            ...mapGetters('results', ['total'])
        },
        methods: {
            ...mapActions('results', ['runSearch', 'getSlug']),
            downloadResults() {
                this.showDownload = true;
                setTimeout(() => {
                    this.showDownload = false;
                }, 1000);
            },
            citeSearch() {
                this.showCite = !this.showCite;
            },
            shareSearch() {
                this.getSlug();
                this.showShare = !this.showShare;
            }
        }
    }
</script>
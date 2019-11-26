<template>
    <div id="result" :class="{disabled: resultsInvalid}">
        <div class="flex-container flex-center flex-column alert-error full-width" v-if="failed">
            <h3>Something went wrong!</h3>
            <p>Please check your query and <a href="/contact">contact us</a> if you think you've
               found a problem.</p>
        </div>
        <div class="flex-container flex-left flex-stretch-first" v-if="hasResult">
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
                        <p>Share this search:</p>
                        <p><span class="nowrap copyable">data.nhm.ac.uk/search/{{ slug }}</span></p>
                        <small class="alert-warning">This link is for social sharing <em>only</em>.
                                                     If you are intending to reference this search
                                                     in a publication, <a href="#">use a
                                                                                   DOI</a>.</small>
                    </div>
                </transition>
                <a href="#" @click="shareSearch" class="btn btn-disabled">
                    <i class="fas"
                        :class="slugLoading ? ['fa-pulse', 'fa-spinner'] : ['fa-share-alt']"></i>Share
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
        <div>
            <ul class="nav nav-tabs">
                <li v-for="viewTab in views" :key="viewTab.id"
                    :class="{active: currentView === viewTab}" @click="currentView = viewTab">
                    <a>{{ viewTab }}</a>
                </li>
            </ul>

            <component :is="viewComponent" v-if="hasRecords"></component>
        </div>

        <div class="pagination-wrapper" v-if="after.length > 0 && !resultsInvalid">
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
    import ListView from './views/ListView.vue';
    import {mapActions, mapGetters, mapState} from 'vuex'

    export default {
        name:       'Results',
        components: {
            TableView,
            ListView
        },
        data:       function () {
            return {
                showDownload: false,
                showCite:     false,
                showShare:    false,
                views:        ['Table', 'List'],
                currentView:  'Table',
                doi:          '',
            }
        },
        computed:   {
            ...mapState('results', ['page', 'after', 'current', 'slug', 'failed',
                                    'resultsLoading', 'slugLoading', 'resultsInvalid']),
            ...mapGetters('results', ['total', 'hasResult', 'hasRecords']),
            viewComponent() {
                return this.currentView + 'View';
            }
        },
        methods:    {
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
                if (!this.showShare && this.slug === null) {
                    this.getSlug();
                }
                else {
                    this.showShare = !this.showShare;
                }
            }
        },
        watch:      {
            slug() {
                this.showShare = this.slug !== null;
            }
        }
    }
</script>
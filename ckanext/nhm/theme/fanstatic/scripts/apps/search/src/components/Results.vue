<template>
    <div id="result" :class="{disabled: resultsInvalid}">
        <div class="flex-container flex-center flex-column alert-error full-width" v-if="failed">
            <h3>Something went wrong!</h3>
            <p>Please check your query and <a href="/contact">contact us</a> if you think you've
               found a problem.</p>
        </div>
        <div class="flex-container flex-left flex-stretch-first" v-if="hasResult">
            <h3>{{ total.toLocaleString('en-GB') }} records</h3>
            <div style="position: relative;">
                <transition name="slidedown">
                    <div class="floating info-popup" v-if="showCite"
                        v-dismiss="{switch: 'showCite', ignore: ['show-cite', 'use-a-doi']}">
                        <p>Cite this search:</p>
                        <p>
                            <a href="#" @click="citeSearch" class="btn btn-primary"
                                v-if="doi === null"><i class="fas"
                                :class="doiLoading ? ['fa-pulse', 'fa-spinner'] : ['fa-pen']"></i>
                                Create a DOI
                            </a>
                        </p>
                        <p class="nowrap copyable" v-if="doi !== null">{{ doi }}</p>
                        <p class="alert-error" v-if="doiFailed">
                            Failed to retrieve DOI. Please try again later.
                        </p>
                    </div>
                </transition>
                <a href="#" @click="showCite = !showCite" class="btn btn-disabled" id="show-cite">
                    <i class="fas fa-book"></i>Cite
                </a>
            </div>
            <div style="position: relative;">
                <transition name="slidedown">
                    <div class="floating info-popup" v-if="showShare"
                        v-dismiss="{switch: 'showShare', ignore: ['show-share']}">
                        <div v-if="slug !== null">
                            <p>Share this search:</p>
                            <p><span class="nowrap copyable">data.nhm.ac.uk/search/{{ slug }}</span>
                            </p>
                            <small class="alert-warning">This link is for social sharing
                                <em>only</em>. If you are intending to reference this search in a
                                                         publication, <a href="#"
                                    @click="citeNotShare" id="use-a-doi">use a DOI</a>.</small>
                        </div>
                        <p class="alert-error" v-if="slugFailed">
                            Failed to retrieve link. Please try again later.
                        </p>
                    </div>
                </transition>
                <a href="#" @click="shareSearch" class="btn btn-disabled" id="show-share">
                    <i class="fas"
                        :class="slugLoading ? ['fa-pulse', 'fa-spinner'] : ['fa-share-alt']"></i>Share
                </a>
            </div>
            <div style="position: relative;">
                <transition name="slidedown">
                    <div class="floating info-popup" v-if="showDownload"
                        v-dismiss="{switch: 'showDownload', ignore: ['show-download']}">
                        Coming soon!
                    </div>
                </transition>
                <a href="#" v-if="total > 0" @click="downloadResults" class="btn btn-disabled"
                    id="show-download">
                    <i class="fas fa-cloud-download-alt"></i>Download
                </a>
            </div>
        </div>
        <div>
            <div class="flex-container flex-stretch-first flex-center">
                <ul class="nav nav-tabs">
                    <li v-for="viewTab in views" :key="viewTab.id"
                        :class="{active: currentView === viewTab}" @click="currentView = viewTab">
                        <a>{{ viewTab }}</a>
                    </li>
                </ul>
                <div class="text-right">
                    <a href="#" @click="showFields = !showFields" :id="'show-fields-' + _uid">
                        <i class="fas fa-plus-circle"></i>
                    </a>
                    <transition name="slidedown">
                        <FieldPicker v-if="showFields" :callback="addCustomHeader"
                            :resource-ids="resultResourceIds"
                            v-dismiss="{switch: 'showFields', ignore: ['show-fields-' + _uid]}">
                        </FieldPicker>
                    </transition>
                </div>
            </div>


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
    import FieldPicker from './misc/FieldPicker.vue';
    import {mapActions, mapGetters, mapMutations, mapState} from 'vuex'

    export default {
        name:       'Results',
        components: {
            TableView,
            ListView,
            FieldPicker
        },
        data:       function () {
            return {
                showDownload: false,
                showCite:     false,
                showShare:    false,
                showFields:   false,
                views:        ['Table', 'List'],
                currentView:  'Table',
            }
        },
        computed:   {
            ...mapState('results', ['page', 'after', 'current', 'slug', 'failed',
                                    'resultsLoading', 'slugLoading', 'resultsInvalid', 'doi',
                                    'doiLoading', 'slugFailed', 'doiFailed']),
            ...mapGetters('results', ['total', 'hasResult', 'hasRecords', 'resultResourceIds']),
            viewComponent() {
                return this.currentView + 'View';
            }
        },
        methods:    {
            ...mapMutations('results', ['addCustomHeader']),
            ...mapActions('results', ['runSearch', 'getSlug', 'getDOI']),
            downloadResults() {
                this.showDownload = true;
                setTimeout(() => {
                    this.showDownload = false;
                }, 1000);
            },
            citeSearch() {
                this.getDOI();
            },
            shareSearch() {
                if (!this.showShare && this.slug === null) {
                    this.getSlug();
                }
                else {
                    this.showShare = !this.showShare;
                }
            },
            citeNotShare() {
                this.showShare = false;
                this.showCite  = true;
            }
        },
        watch:      {
            slug() {
                this.showShare = this.slug !== null;
            },
            slugFailed(fail) {
                if (fail) {
                    this.showShare = true;
                }
            }
        }
    }
</script>
<template>
    <div id="result">
        <Loading v-if="status.resultData.loading"></Loading>
        <LoadError v-if="status.resultData.failed">
            <h3>Something went wrong!</h3>
            <p>Please check your query and <a href="/contact">contact us</a> if you think you've
               found a problem.</p>
        </LoadError>
        <div class="flex-container flex-left flex-stretch-first" v-if="hasResult" :class="{disabled: invalidated}">
            <h3>{{ total.toLocaleString('en-GB') }} records</h3>
            <div class="info-popup-button">
                <transition name="slidedown">
                    <div class="floating info-popup doi-popup"
                         v-if="showCite"
                         v-dismiss="{switch: 'showCite', ignore: ['#show-cite', 'use-a-doi']}">
                        <p>Cite this search:</p>
                        <Copyable :copy-text="'https://doi.org/' + doi" v-if="doi !== null">
                            <span class="nowrap">{{ doi }}</span>
                        </Copyable>
                        <p class="alert-error" v-if="status.doi.failed">
                            Failed to retrieve DOI. Please try again later. </p>
                        <div class="form-row" v-if="doi === null">
                            <label for="doi-email" class="control-label">
                                <span class="control-required">*</span>Your email </label>
                            <input id="doi-email"
                                   type="text"
                                   class="full-width"
                                   v-model="doiForm.email_address"
                                   placeholder="data@nhm.ac.uk">
                        </div>
                        <div class="privacy-warning">
                            <p><i>Data Protection</i></p>
                            <p>The Natural History Museum will use your personal data in accordance
                               with data protection legislation to process your requests. For more
                               information please read our <a href="/privacy">privacy notice</a>.
                            </p>
                        </div>
                        <div class="text-right">
                            <a href="#"
                               @click="getDOI(doiForm)"
                               class="btn btn-primary"
                               v-if="doi === null"><i class="fas"
                                                      :class="status.doi.loading ? ['fa-pulse', 'fa-spinner'] : ['fa-pen']"></i>
                                Create a DOI </a>
                        </div>
                    </div>
                </transition>
                <a href="#" @click="showCite = !showCite" class="btn btn-disabled" id="show-cite">
                    <i class="fas fa-book"></i>Cite </a>
            </div>
            <div class="info-popup-button">
                <transition name="slidedown">
                    <div class="floating info-popup"
                         v-if="showShare"
                         v-dismiss="{switch: 'showShare', ignore: ['#show-share']}">
                        <div v-if="slug !== null">
                            <p>Share this search:</p>
                            <Copyable :copy-text="'https://' + shareUrl" :display-text="shareUrl">
                                <span class="nowrap">{{ shareUrl }}</span>
                            </Copyable>
                            <small class="alert-warning">This link is for social sharing
                                <em>only</em>. If you are intending to reference this search in a
                                                         publication, <a href="#"
                                                                         @click="citeNotShare"
                                                                         id="use-a-doi">use a
                                                                                        DOI</a>.</small>
                        </div>
                        <p class="alert-error" v-if="status.slug.failed">
                            Failed to retrieve link. Please try again later. </p>
                    </div>
                </transition>
                <a href="#" @click="shareSearch" class="btn btn-disabled" id="show-share">
                    <i class="fas"
                       :class="status.slug.loading ? ['fa-pulse', 'fa-spinner'] : ['fa-share-alt']"></i>Share
                </a>
            </div>
            <div class="info-popup-button">
                <transition name="slidedown">
                    <div class="floating info-popup download-popup"
                         v-if="showDownload"
                         v-dismiss="{switch: 'showDownload', ignore: ['#show-download']}">
                        <p v-if="download !== null">
                            Success! You should receive an email at <b>{{ downloadForm.email_address
                                                                       }}</b> soon. </p>
                        <p class="alert-error" v-if="status.download.failed">
                            The download request failed. Please try again later. </p>
                        <div v-if="download === null">
                            <p>The data will be extracted, with current filters applied, and sent to
                               the given email address shortly.</p>
                            <div class="form-row">
                                <label for="download-email" class="control-label">
                                    <span class="control-required">*</span>Your email </label>
                                <input id="download-email"
                                       type="text"
                                       class="full-width"
                                       v-model="downloadForm.email_address"
                                       placeholder="data@nhm.ac.uk">
                            </div>
                            <div class="form-row">
                                <label for="download-format">File format</label>
                                <select id="download-format"
                                        v-model="downloadForm.format"
                                        class="full-width">
                                    <option>csv</option>
                                </select>
                            </div>
                            <div class="form-row flex-container flex-wrap flex-between">
                                <div>
                                    <label for="download-sep">One file per resource</label> <input
                                    id="download-sep"
                                    type="checkbox"
                                    v-model="downloadForm.separate_files">
                                </div>
                                <div>
                                    <label for="download-empty">Skip empty columns</label>
                                    <input id="download-empty"
                                           type="checkbox"
                                           v-model="downloadForm.ignore_empty_fields">
                                </div>
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
                               @click="getDownload(downloadForm)"> <i class="fas"
                                                                      :class="status.download.loading ? ['fa-pulse', 'fa-spinner'] : ['fa-download']"></i>
                                Request Download </a>
                        </div>
                    </div>
                </transition>
                <a href="#"
                   v-if="total > 0"
                   @click="showDownload = !showDownload"
                   class="btn btn-disabled"
                   id="show-download"> <i class="fas fa-cloud-download-alt"></i>Download </a>
            </div>
        </div>
        <div v-if="hasResult" :class="{disabled: invalidated}">
            <div class="flex-container flex-stretch-first flex-center">
                <ul class="nav nav-tabs">
                    <li v-for="viewTab in views"
                        :key="viewTab.id"
                        :class="{active: view === viewTab}"
                        @click="setView(viewTab)">
                        <a>{{ viewTab }}</a>
                    </li>
                </ul>
                <div class="text-right">
                    <a href="#" @click="showFields = !showFields" :id="'show-fields-' + _uid"> <i
                        class="fas fa-plus-circle"></i> </a>
                    <transition name="slidedown">
                        <FieldPicker v-if="showFields"
                                     :callback="addCustomHeader"
                                     :resource-ids="resultResourceIds"
                                     :classes="['floating']"
                                     v-dismiss="{switch: 'showFields', ignore: ['#show-fields-' + _uid]}"></FieldPicker>
                    </transition>
                </div>
            </div>

            <div>
                <component :is="viewComponent" v-if="hasRecords"></component>
            </div>
        </div>

        <div class="pagination-wrapper" v-if="after.length > 0 && !invalidated" :class="{disabled: invalidated}">
            <ul class="pagination">
                <li v-if="page > 0">
                    <a href="#" @click="runSearch(0)"><i class="fas fa-angle-double-left"></i></a>
                </li>
                <li v-if="page > 0">
                    <a href="#" @click="runSearch(page - 1)">{{ page }}</a>
                </li>
                <li class="active">
                    <a href="#">{{ page + 1 }}</a>
                </li>
                <li v-if="after.length > page">
                    <a href="#" @click="runSearch(page + 1)">{{ page + 2}}</a>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
    import TableView from './views/TableView.vue';
    import ListView from './views/ListView.vue';
    import GalleryView from './views/GalleryView.vue';
    import FieldPicker from './misc/FieldPicker.vue';
    import {mapActions, mapGetters, mapMutations, mapState} from 'vuex'
    import Copyable from './misc/Copyable.vue';
    import Loading from './Loading.vue';
    import LoadError from './LoadError.vue'

    export default {
        name:       'Results',
        components: {
            Copyable,
            TableView,
            ListView,
            GalleryView,
            FieldPicker,
            LoadError,
            Loading
        },
        data:       function () {
            return {
                showDownload: false,
                showCite:     false,
                showShare:    false,
                showFields:   false,
                views:        ['Table', 'List', 'Gallery'],
                doiForm:      {
                    email_address: null
                },
                downloadForm: {
                    email_address:       null,
                    format:              'csv',
                    separate_files:      true,
                    ignore_empty_fields: true
                }
            }
        },
        computed:   {
            ...mapState('results', ['resultData', 'page', 'after', 'status', 'slug', 'doi', 'download', 'invalidated']),
            ...mapState('results/display', ['view', 'headers']),
            ...mapGetters('results', ['total', 'hasResult', 'hasRecords', 'resultResourceIds']),
            viewComponent() {
                return this.view + 'View';
            },
            shareUrl() {
                return `data.nhm.ac.uk/search/${this.slug}`;
            }
        },
        methods:    {
            ...mapMutations('results/display', ['addCustomHeader', 'setView']),
            ...mapActions('results', ['runSearch', 'getSlug', 'getDOI', 'getDownload']),
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
        },
    }
</script>
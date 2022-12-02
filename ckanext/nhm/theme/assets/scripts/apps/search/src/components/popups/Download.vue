<template>
    <Popup classes="download-popup" icon="fa-cloud-download-alt" label="Download"
           popup-id="show-download" :parent-toggle="showPopup" v-on:toggle="toggle">
        <p v-if="download !== null">
            Success! Check the <a :href="statusPage">status page</a> to follow your download's progress.
        </p>
        <p class="alert-error" v-if="status.download.failed">
            The download request failed. Please try again later. </p>
        <div v-if="download === null">
            <div class="form-group">
                <div class="form-row">
                    <label for="download-format">File format</label>
                    <select id="download-format" @change="setFileDefaults"
                            v-model="downloadForm.file.format"
                            class="full-width">
                        <option value="csv">CSV/TSV</option>
                        <option value="dwc">Darwin Core</option>
                        <option value="xlsx">Excel (XLSX)</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                <div class="form-row flex-container flex-wrap flex-between">
                    <div class="no-pad-h">
                        <label for="download-sep">One file per resource</label>
                        <input
                            id="download-sep"
                            type="checkbox"
                            v-model="downloadForm.file.separate_files">
                    </div>
                    <div class="no-pad-h">
                        <label for="download-empty">Skip empty columns</label>
                        <input id="download-empty"
                               type="checkbox"
                               v-model="downloadForm.file.ignore_empty_fields">
                    </div>
                </div>
                <template v-if="downloadForm.file.format === 'csv'">
                    <div class="form-row">
                        <label for="download-csv-delimiter">Delimiter</label>
                        <select id="download-csv-delimiter" class="full-width"
                                v-model="downloadForm.file.format_args['delimiter']">
                            <option value="comma">Comma</option>
                            <option value="tab">Tab</option>
                        </select>
                    </div>
                </template>
                <template v-else-if="downloadForm.file.format === 'dwc'">
                    <div class="form-row">
                        <label for="download-dwc-core-ext">Core extension</label>
                        <select id="download-dwc-core-ext" class="full-width"
                                v-model="downloadForm.file.format_args['core_extension_name']">
                            <option value="gbif_occurrence">GBIF Occurrence (default)</option>
                            <option value="gbif_taxon">GBIF Taxon</option>
                            <option value="gbif_event">GBIF Event</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <label for="download-dwc-exts">Extensions</label>
                        <select id="download-dwc-exts" class="full-width" multiple
                                v-model="downloadForm.file.format_args['extension_names']">
                            <option value="gbif_multimedia">GBIF Multimedia</option>
                        </select>
                    </div>
                </template>
            </div>

            <div class="form-group">
                <div class="form-row">
                    <label for="download-notifier">
                        Notification type
                    </label>
                    <p><small>How should we notify you when your download is ready?</small></p>
                    <select id="download-notifier"
                            class="full-width"
                            v-model="downloadForm.notifier.type" @change="setNotifierDefaults">
                        <option value="email">Email</option>
                        <option value="webhook">External webhook (e.g. IFTTT, Discord)</option>
                        <option value="none">None; I'll check the download status manually</option>
                    </select>
                </div>
                <template v-if="downloadForm.notifier.type === 'email'">
                    <div class="form-row">
                        <label for="download-email">
                            Email address
                        </label>
                        <input id="download-email"
                               type="text"
                               class="full-width"
                               v-model="downloadForm.notifier.type_args['emails']"
                               placeholder="data@nhm.ac.uk">
                    </div>
                </template>
                <template v-else-if="downloadForm.notifier.type === 'webhook'">
                    <div class="form-row">
                        <label for="download-webhook-url">
                            Webhook URL
                        </label>
                        <input id="download-webhook-url"
                               type="text"
                               class="full-width"
                               v-model="downloadForm.notifier.type_args['url']">
                    </div>
                    <div class="form-row">
                        <label for="download-webhook-url-param">
                            URL parameter name
                        </label>
                        <input id="download-webhook-url-param"
                               type="text"
                               class="full-width"
                               v-model="downloadForm.notifier.type_args['url_param']">
                    </div>
                    <div class="form-row">
                        <label for="download-webhook-text-param">
                            Text parameter name
                        </label>
                        <input id="download-webhook-text-param"
                               type="text"
                               class="full-width"
                               v-model="downloadForm.notifier.type_args['text_param']">
                    </div>
                    <small>This posts status updates in JSON format to the given URL.</small>
                </template>
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
            <a href="#" class="btn btn-primary text-right" @click="getDownload(downloadForm)"><i
                class="fas"
                :class="status.download.loading ? ['fa-pulse', 'fa-spinner'] : ['fa-download']"></i>
                Request Download
            </a>
        </div>
    </Popup>
</template>

<script>
import BasePopup from './BasePopup.vue';
import { mapActions, mapState } from 'vuex';

export default {
    name: 'Download',
    extends: BasePopup,
    data: function () {
        return {
            downloadForm: {
                file: {
                    format: 'csv',
                    separate_files: true,
                    ignore_empty_fields: true,
                    format_args: {}
                },
                notifier: {
                    type: 'email',
                    type_args: {}
                }
            },
        };
    },
    computed: {
        ...mapState('results', ['download', 'downloadId']),
        statusPage() {
            if (this.downloadId !== null) {
                return `/status/download/${this.downloadId}`;
            }
        }
    },
    methods: {
        ...mapActions('results', ['getDownload']),
        setFileDefaults() {
            let formatArgs = {};

            switch (this.downloadForm.file.format) {
                case 'csv':
                    formatArgs = {
                        delimiter: 'comma'
                    };
                    break;
                case 'dwc':
                    formatArgs = {
                        extension_names: ['gbif_multimedia'],
                        core_extension_name: 'gbif_occurrence'
                    };
                    break;
            }

            this.$set(this.downloadForm.file, 'format_args', formatArgs);
        },
        setNotifierDefaults() {
            let typeArgs = {};

            switch (this.downloadForm.notifier.type) {
                case 'email':
                    typeArgs = {
                        email: ''
                    };
                    break;
                case 'webhook':
                    typeArgs = {
                        url: '',
                        url_param: 'url',
                        text_param: 'text',
                        post: false
                    };
                    break;
            }

            this.$set(this.downloadForm.notifier, 'type_args', typeArgs);
        }
    },
    created() {
        this.setFileDefaults();
        this.setNotifierDefaults();
    }
};
</script>

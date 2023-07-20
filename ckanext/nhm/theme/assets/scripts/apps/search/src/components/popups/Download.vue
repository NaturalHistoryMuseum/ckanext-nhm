<template>
  <Popup
    classes="download-popup"
    icon="fa-cloud-download-alt"
    label="Download"
    popup-id="show-download"
    :parent-toggle="showPopup"
    v-on:toggle="toggle"
  >
    <div v-show="download !== null">
      <!-- the download is set to null *before* the dismiss method runs, so if v-if
            is used instead of v-show, the dismiss method can't find these buttons inside
            the main popup and assumes they're outside of it. -->
      <p v-if="download !== null">
        Success! Check the <a :href="statusPage">status page</a> to follow your
        download's progress.
      </p>
      <div class="flex-container flex-around pad-v">
        <a
          :href="statusPage"
          class="btn btn-primary text-right"
          v-if="download !== null"
          ><i class="fas fa-hourglass-half"></i>
          Download status
        </a>
        <a
          href="javascript:void(0);"
          class="btn btn-primary text-right"
          @click="resetPopup"
          ><i class="fas fa-undo-alt"></i>
          New download
        </a>
      </div>
    </div>
    <p
      class="alert-error"
      v-if="status.download.failed || formErrors.length > 0"
    >
      {{ errorMessage }}
    </p>
    <div v-if="download === null">
      <div class="form-group">
        <div class="form-row">
          <label for="download-format">File format</label>
          <select
            id="download-format"
            @change="setFileDefaults"
            v-model="downloadForm.file.format"
            class="full-width-input"
          >
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
              v-model="downloadForm.file.separate_files"
            />
          </div>
          <div class="no-pad-h">
            <label for="download-empty">Skip empty columns</label>
            <input
              id="download-empty"
              type="checkbox"
              v-model="downloadForm.file.ignore_empty_fields"
            />
          </div>
        </div>
        <div
          @click="showAdvanced = !showAdvanced"
          v-if="['csv', 'dwc'].includes(downloadForm.file.format)"
          class="advanced-options-divider"
        >
          <b>Advanced Options</b>
          <i
            class="inline-icon-left fas"
            :class="showAdvanced ? 'fa-caret-up' : 'fa-caret-down'"
          ></i>
        </div>
        <template v-if="showAdvanced">
          <template v-if="downloadForm.file.format === 'csv'">
            <div class="form-row">
              <label for="download-csv-delimiter">Delimiter</label>
              <select
                id="download-csv-delimiter"
                class="full-width-input"
                v-model="downloadForm.file.format_args['delimiter']"
              >
                <option value="comma">Comma</option>
                <option value="tab">Tab</option>
              </select>
            </div>
          </template>
          <template v-else-if="downloadForm.file.format === 'dwc'">
            <div class="form-row">
              <label for="download-dwc-core-ext">Core extension</label>
              <select
                id="download-dwc-core-ext"
                class="full-width-input"
                v-model="downloadForm.file.format_args['core_extension_name']"
              >
                <option value="gbif_occurrence">
                  GBIF Occurrence (default)
                </option>
                <option value="gbif_taxon">GBIF Taxon</option>
                <option value="gbif_event">GBIF Event</option>
                <option value="none">None</option>
              </select>
            </div>
            <div class="form-row">
              <b>Extensions:</b>
              <div class="input-list">
                <div v-for="(ext, name) in dwcExtensions">
                  <label :for="name">{{ ext.label }}</label>
                  <input
                    type="checkbox"
                    :value="name"
                    :id="name"
                    v-model="downloadForm.file.format_args['extension_names']"
                  />
                </div>
              </div>
            </div>
            <div
              class="form-row"
              v-if="downloadForm.file.format_args['extension_names'].length > 0"
            >
              <b>Extension fields:</b>
              <p>
                <small
                  >Which fields contain the extension data? (comma-separated
                  list)</small
                >
              </p>
              <div class="input-list">
                <template
                  v-for="name in downloadForm.file.format_args[
                    'extension_names'
                  ]"
                >
                  <label :for="name + '-fields'">{{
                    dwcExtensions[name].label
                  }}</label>
                  <input
                    type="text"
                    :id="name + '-fields'"
                    v-model="dwcExtensions[name].fields"
                  />
                </template>
              </div>
            </div>
            <div class="form-row">
              <small
                >See <a href="https://dwc.tdwg.org" target="_blank">TDWG</a> and
                <a href="https://www.gbif.org/darwin-core" target="_blank"
                  >GBIF</a
                >
                for more details on the Darwin Core format and what
                <a href="https://rs.gbif.org" target="_blank"
                  >these extensions</a
                >
                are.</small
              >
            </div>
          </template>
        </template>
      </div>

      <div class="form-group">
        <div class="form-row">
          <label for="download-notifier"> Notification type </label>
          <p>
            <small>How should we notify you when your download is ready?</small>
          </p>
          <select
            id="download-notifier"
            class="full-width-input"
            v-model="downloadForm.notifier.type"
            @change="setNotifierDefaults"
          >
            <option value="email">Email</option>
            <option value="webhook">
              External webhook (e.g. IFTTT, Discord)
            </option>
            <option value="none">
              None; I'll check the download status manually
            </option>
          </select>
        </div>
        <template v-if="downloadForm.notifier.type === 'email'">
          <div class="form-row">
            <label for="download-email"> Email address(es) </label>
            <input
              id="download-email"
              type="text"
              class="full-width-input"
              v-model="downloadForm.notifier.type_args['emails']"
              placeholder="data@nhm.ac.uk"
            />
            <p>
              <small
                >Multiple email addresses can be added as a comma-separated
                list.</small
              >
            </p>
          </div>
        </template>
        <template v-else-if="downloadForm.notifier.type === 'webhook'">
          <div class="form-row">
            <label for="download-webhook-url"> Webhook URL </label>
            <input
              id="download-webhook-url"
              type="text"
              class="full-width-input"
              v-model="downloadForm.notifier.type_args['url']"
            />
          </div>
          <div class="form-row">
            <label for="download-webhook-url-param"> URL parameter name </label>
            <input
              id="download-webhook-url-param"
              type="text"
              class="full-width-input"
              v-model="downloadForm.notifier.type_args['url_param']"
            />
          </div>
          <div class="form-row">
            <label for="download-webhook-text-param">
              Text parameter name
            </label>
            <input
              id="download-webhook-text-param"
              type="text"
              class="full-width-input"
              v-model="downloadForm.notifier.type_args['text_param']"
            />
          </div>
          <small
            >This posts status updates in JSON format to the given URL.</small
          >
        </template>
      </div>
    </div>
    <div class="privacy-warning">
      <p><i>Data Protection</i></p>
      <p>
        The Natural History Museum will use your personal data in accordance
        with data protection legislation to process your requests. For more
        information please read our <a href="/privacy">privacy notice</a>.
      </p>
    </div>
    <div class="text-right" v-if="download === null">
      <a
        href="javascript:void(0);"
        class="btn btn-primary text-right"
        @click="submitForm"
        ><i
          class="fas"
          :class="
            status.download.loading
              ? ['fa-pulse', 'fa-spinner']
              : ['fa-download']
          "
        ></i>
        Request Download
      </a>
    </div>
  </Popup>
</template>

<script>
import BasePopup from './BasePopup.vue';
import { mapActions, mapState } from 'vuex';
import { trim } from 'core-js/internals/string-trim';

export default {
  name: 'Download',
  extends: BasePopup,
  data: function () {
    return {
      formErrors: [],
      downloadForm: {
        file: {
          format: 'csv',
          separate_files: true,
          ignore_empty_fields: true,
          format_args: {},
        },
        notifier: {
          type: 'email',
          type_args: {},
        },
      },
      showAdvanced: false,
      dwcExtensions: {
        // this is essentially duplicated from dwc/urls.py in vds
        gbif_multimedia: {
          label: 'GBIF Multimedia',
          fields: 'associatedMedia', // this should be a comma-separated list
        },
        gbif_vernacular: {
          label: 'GBIF Vernacular',
          fields: 'vernacularName',
        },
        gbif_references: {
          label: 'GBIF References',
          fields: 'references',
        },
        gbif_description: {
          label: 'GBIF Description',
          fields: 'taxonDescription',
        },
        gbif_distribution: {
          label: 'GBIF Distribution',
          fields: 'locality',
        },
        gbif_species_profile: {
          label: 'GBIF Species Profile',
          fields: 'speciesProfile',
        },
        gbif_types_and_specimen: {
          label: 'GBIF Types and Specimen',
          fields: 'typeStatus',
        },
        gbif_identifier: {
          label: 'GBIF Identifier',
          fields: 'verbatimIdentification',
        },
      },
    };
  },
  computed: {
    ...mapState('results', ['download', 'downloadId']),
    statusPage() {
      if (this.downloadId !== null) {
        return `/status/download/${this.downloadId}`;
      }
    },
    errorMessage() {
      if (this.formErrors.length === 0) {
        return 'The download request failed. Please try again later.';
      } else {
        return this.formErrors.join('; ');
      }
    },
  },
  methods: {
    ...mapActions('results', ['getDownload', 'resetDownload']),

    resetPopup() {
      this.resetDownload();
    },

    setFileDefaults() {
      let formatArgs = {};

      switch (this.downloadForm.file.format) {
        case 'csv':
          formatArgs = {
            delimiter: 'comma',
          };
          break;
        case 'dwc':
          formatArgs = {
            extension_names: ['gbif_multimedia'],
            core_extension_name: 'gbif_occurrence',
            extension_map: {},
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
            emails: '',
          };
          break;
        case 'webhook':
          typeArgs = {
            url: '',
            url_param: 'url',
            text_param: 'text',
            post: false,
          };
          break;
      }

      this.$set(this.downloadForm.notifier, 'type_args', typeArgs);
    },
    validateForm() {
      this.formErrors = [];
      if (this.downloadForm.notifier.type === 'email') {
        if (
          !this.downloadForm.notifier.type_args ||
          !this.downloadForm.notifier.type_args.emails
        ) {
          this.formErrors.push('Email address must be provided');
        } else {
          let emails = this.downloadForm.notifier.type_args.emails
            .split(',')
            .map(trim);
          let emailRegex =
            /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          emails.forEach((e) => {
            if (!emailRegex.test(e)) {
              this.formErrors.push(`${e} is not a valid email address`);
            }
          });
        }
      }
      return this.formErrors.length === 0;
    },
    submitForm() {
      if (!this.validateForm()) {
        return;
      }

      // any pre-submission processing goes here
      if (this.downloadForm.file.format === 'dwc') {
        if (this.downloadForm.file.format_args.core_extension_name === 'none') {
          // remove any mention of core extensions if user has picked "none"
          delete this.downloadForm.file.format_args.core_extension_name;
        }

        this.downloadForm.file.format_args.extension_names.forEach((e) => {
          // add fields to specify where the nested extension data is
          this.downloadForm.file.format_args.extension_map[e] =
            this.dwcExtensions[e].fields.split(',');
        });
      }

      if (this.downloadForm.notifier.type === 'email') {
        this.downloadForm.notifier.type_args.emails =
          this.downloadForm.notifier.type_args.emails.split(',').map(trim);
      }

      this.getDownload(this.downloadForm);
    },
  },
  created() {
    this.setFileDefaults();
    this.setNotifierDefaults();
  },
};
</script>

<template>
  <Popup
    classes="doi-popup"
    icon="fa-book"
    label="Cite"
    popup-id="show-cite"
    :parent-toggle="showPopup"
    v-on:toggle="toggle"
  >
    <p>Cite this search:</p>
    <Copyable :copy-text="'https://doi.org/' + doi" v-if="doi !== null">
      <span class="nowrap">{{ doi }}</span>
    </Copyable>
    <p class="alert-error" v-if="status.doi.failed">
      Failed to retrieve DOI. Please try again later.
    </p>
    <div class="form-row" v-if="doi === null">
      <label for="doi-email" class="control-label">
        <span class="control-required">*</span>
        Your email
      </label>
      <input
        id="doi-email"
        type="text"
        class="full-width"
        v-model="doiForm.email_address"
        placeholder="data@nhm.ac.uk"
      />
    </div>
    <div class="privacy-warning">
      <p><i>Data Protection</i></p>
      <p>
        The Natural History Museum will use your personal data in accordance
        with data protection legislation to process your requests. For more
        information please read our
        <a href="/privacy">privacy notice</a>
        .
      </p>
    </div>
    <div class="text-right">
      <a
        href="javascript:void(0);"
        @click="getDOI(doiForm)"
        class="btn btn-primary"
        v-if="doi === null"
        ><i
          class="fas"
          :class="status.doi.loading ? ['fa-pulse', 'fa-spinner'] : ['fa-pen']"
        ></i>
        Create a DOI
      </a>
    </div>
  </Popup>
</template>

<script>
import BasePopup from './BasePopup.vue';
import { mapActions, mapState } from 'vuex';

export default {
  name: 'Cite',
  extends: BasePopup,
  data: function () {
    return {
      doiForm: {
        email_address: null,
      },
    };
  },
  computed: {
    ...mapState('results', ['doi']),
  },
  methods: {
    ...mapActions('results', ['getDOI']),
  },
};
</script>

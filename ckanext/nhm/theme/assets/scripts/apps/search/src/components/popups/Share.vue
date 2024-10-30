<template>
  <Popup
    classes="share-popup"
    :icon="status.slug.loading ? 'fa-pulse fa-spinner' : 'fa-share-alt'"
    label="Share"
    popup-id="show-share"
    :parent-toggle="showPopup"
    v-on:toggle="toggle"
  >
    <div v-if="slug !== null">
      <p>Share this search:</p>
      <Copyable
        :copy-text="'https://' + shareUrl"
        :display-text="shareUrl"
        :edit-button="canEditSlug"
        @edit="showEditSlug = !showEditSlug"
      >
        <span
          :style="{
            minWidth: (22 + slug.length) * 9.6 + 'px',
            width: '100%',
            wordBreak: 'break-all',
            opacity: showEditSlug ? 0.5 : 1,
          }"
          >{{ shareUrl }}</span
        >
      </Copyable>
      <Editable
        :edit-text="slug"
        :edit-status="status.slugEdit"
        v-if="showEditSlug"
        @save="saveSlugEdit"
      />
      <div class="form-row flex-container flex-wrap flex-around">
        <div v-if="page > 0">
          <label for="chkSharePage">Include page</label>
          <input type="checkbox" id="chkSharePage" v-model="includeSharePage" />
        </div>
        <div>
          <label for="chkShareView">Include view</label>
          <input type="checkbox" id="chkShareView" v-model="includeShareView" />
        </div>
      </div>
      <div class="alert-warning share-popup-warning">
        <small
          >This link is for social sharing <em>only</em>. If you are intending
          to reference this search in a publication, use a DOI.
        </small>
      </div>
    </div>
    <p class="alert-error" v-if="status.slug.failed">
      Failed to retrieve link. Please try again later.
    </p>
    <div v-if="slug === null && !status.slug.failed">Loading...</div>
  </Popup>
</template>

<script>
import BasePopup from './BasePopup.vue';
import { mapActions, mapState } from 'vuex';

export default {
  name: 'Share',
  extends: BasePopup,
  data: function () {
    return {
      includeSharePage: false,
      includeShareView: false,
      showEditSlug: false,
      user: {
        loggedIn: false,
        sysAdmin: false,
      },
    };
  },
  computed: {
    ...mapState('results', ['slug', 'slugReserved', 'page']),
    ...mapState('results/display', ['view']),
    shareUrl() {
      let Url = `data.nhm.ac.uk/search/${this.slug}`;

      let params = [];
      if (this.includeShareView) {
        params.push(`view=${this.view.toLowerCase()}`);
      }
      if (this.includeSharePage && this.pageParam !== '') {
        params.push(`page=${this.pageParam}`);
      }
      if (params.length > 0) {
        Url += `?${params.join('&')}`;
      }
      return Url;
    },
    canEditSlug() {
      if (this.slug === null) {
        return false;
      }
      if (this.slugReserved && !this.user.sysAdmin) {
        return false;
      }
      return this.user.loggedIn;
    },
  },
  methods: {
    ...mapActions(['getUser']),
    ...mapActions('results', ['getSlug', 'editSlug']),
    async shareSearch() {
      if (!this.user.loggedIn) {
        await this.getUser().then((u) => {
          this.$set(this, 'user', u);
        });
      }
      if (this.slug === null) {
        this.getSlug();
      }
    },
    saveSlugEdit(newSlug) {
      this.editSlug(newSlug).then(() => {
        this.showEditSlug = false;
      });
    },
    toggle(event) {
      this.shareSearch();
      this.showPopup = event && this.slug !== null;
    },
  },
  watch: {
    slug() {
      this.showPopup = this.slug !== null;
    },
    slugFailed(fail) {
      if (fail) {
        this.showShare = true;
      }
    },
  },
};
</script>

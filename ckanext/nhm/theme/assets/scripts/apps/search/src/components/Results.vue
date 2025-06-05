<template>
  <div id="result">
    <Loading v-if="status.resultData.loading"></Loading>
    <LoadError v-if="status.resultData.failed">
      <h3>Something went wrong!</h3>
      <p>
        Please
        <a href="javascript:void(0);" @click="$emit('show-query')"
          >check your query</a
        >
        ,
        <a href="javascript:void(0);" @click="$emit('reset')">try resetting</a>
        , and
        <a href="/contact">contact us</a>
        if you think you've found a problem.
      </p>
    </LoadError>
    <div
      class="flex-container flex-left flex-stretch-first results-header"
      v-if="hasResult"
      :class="{ disabled: invalidated }"
    >
      <div class="records-total">
        <h3>{{ filteredRecordHeader(total) }}</h3>
        <small class="filtered-total">
          <template v-if="total > 0"
            >showing {{ page * 100 + 1 }}-{{ page * 100 + records.length }}
          </template>
          <template v-else>0</template>
          of
          {{ recordHeader(unfilteredTotal) }} total
        </small>
      </div>
      <!--BUTTONS-->
      <Cite />
      <Share />
      <Download v-if="total > 0" />
    </div>
    <div v-show="hasResult" :class="{ disabled: invalidated }" key="resultView">
      <div class="flex-container flex-stretch-first flex-center">
        <ul class="nav nav-tabs">
          <li
            v-for="viewTab in views"
            :key="viewTab.id"
            :class="{ active: view === viewTab }"
            @click="setView(viewTab)"
          >
            <a>{{ viewTab }}</a>
          </li>
        </ul>
        <div class="text-right">
          <a
            href="javascript:void(0);"
            @click="showFields = !showFields"
            :id="'show-fields-' + _uid"
            v-if="view === 'Table'"
            aria-label="Add fields to results table"
          >
            <i class="fas fa-plus-circle"></i>
          </a>
          <transition name="slidedown">
            <FieldPicker
              v-if="showFields"
              :callback="addCustomHeader"
              :resource-ids="resultResourceIds"
              :classes="['floating', 'header-picker']"
              v-dismiss="{
                switch: 'showFields',
                ignore: ['#show-fields-' + _uid],
              }"
              :selected-fields="headers.flat(1)"
            ></FieldPicker>
          </transition>
        </div>
      </div>

      <div>
        <component :is="viewComponent" v-show="hasRecords"></component>
      </div>
    </div>
    <div v-if="hasResult && total === 0 && !invalidated" class="pad-h pad-v">
      <small
        >Try removing some filters, or use different search terms. Have a look
        at our <a href="/help/search">search help</a> page to learn more about
        how searches are constructed.</small
      >
    </div>

    <div
      class="pagination-wrapper"
      v-if="_after.length > 0 && !invalidated"
      :class="{ disabled: invalidated }"
    >
      <ul class="pagination">
        <li v-if="page > 0">
          <a
            href="javascript:void(0);"
            aria-label="Show first results page"
            @click="runSearch(0)"
          >
            <i class="fas fa-angle-double-left"></i>
          </a>
        </li>
        <li v-if="page > 0">
          <a
            href="javascript:void(0);"
            aria-label="Show previous results page"
            @click="runSearch(page - 1)"
          >
            {{ page }}
          </a>
        </li>
        <li class="active">
          <a
            href="javascript:void(0);"
            aria-label="Go to the top of this results page"
          >
            {{ page + 1 }}
          </a>
        </li>
        <li v-if="_after.length > page">
          <a
            href="javascript:void(0);"
            aria-label="Show next results page"
            @click="runSearch(page + 1)"
          >
            {{ page + 2 }}
          </a>
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
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
import Copyable from './misc/Copyable.vue';
import Loading from './Loading.vue';
import LoadError from './LoadError.vue';
import Editable from './misc/Editable.vue';
import Download from './popups/Download.vue';
import Share from './popups/Share.vue';
import Cite from './popups/Cite.vue';

export default {
  name: 'Results',
  components: {
    Editable,
    Copyable,
    TableView,
    ListView,
    GalleryView,
    FieldPicker,
    LoadError,
    Loading,
    Download,
    Share,
    Cite,
  },
  data: function () {
    return {
      showFields: false,
      views: ['Table', 'List', 'Gallery'],
    };
  },
  computed: {
    ...mapState('results', [
      'resultData',
      'page',
      '_after',
      'invalidated',
      'unfilteredTotal',
    ]),
    ...mapState('results/display', ['view', 'headers']),
    ...mapState('appState', ['status']),
    ...mapGetters('results', [
      'total',
      'hasResult',
      'hasRecords',
      'resultResourceIds',
      'records',
      'pageParam',
    ]),
    ...mapGetters('results/display', ['recordHeader', 'filteredRecordHeader']),
    viewComponent() {
      return this.view + 'View';
    },
  },
  methods: {
    ...mapMutations('results/display', [
      'addCustomHeader',
      'setView',
      'resetFilteredRecordTag',
    ]),
    ...mapActions('results/query/filters', ['deleteTemporaryFilters']),
    ...mapActions('results', ['runSearch']),
  },
  watch: {
    view() {
      this.deleteTemporaryFilters().then((deleteCount) => {
        if (deleteCount > 0) {
          this.runSearch(this.page);
        }
      });
      this.resetFilteredRecordTag();
    },
  },
};
</script>

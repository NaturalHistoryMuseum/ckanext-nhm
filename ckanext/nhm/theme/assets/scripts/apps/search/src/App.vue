<template>
  <div>
    <Loading v-if="app.loading"></Loading>
    <LoadError v-if="app.error"></LoadError>
    <ImageViewer v-if="showImage"></ImageViewer>
    <div class="search-form multisearch-form" v-if="!app.loading && !app.error">
      <div
        class="multisearch-simple flex-container flex-stretch-first flex-smallwrap space-children-v flex-right"
      >
        <div class="search-input control-group search-giant">
          <label for="all" class="sr-only">Search</label>
          <input
            type="text"
            class="search"
            name="all"
            id="all"
            value=""
            autocomplete="off"
            placeholder="Search all fields"
            role="searchbox"
            v-model="search"
            @keyup.enter="runSearch(0)"
          />
          <button type="submit" @click="runSearch(0)">
            <i class="fas fa-search"></i> <span class="sr-only">Search</span>
          </button>
        </div>
        <div class="flex-container flex-nowrap">
          <div class="text-right nowrap" style="margin-left: 10px">
            <a href="/help/search" target="_blank" class="collapse-to-icon">
              Help <i class="fas inline-icon-right fa-question"></i>
            </a>
          </div>
          <div class="text-right nowrap" style="margin-left: 10px">
            <a
              href="javascript:void(0);"
              @click="showAdvanced = !showAdvanced"
              class="collapse-to-icon"
            >
              Advanced
              <i
                class="fas inline-icon-right"
                :class="showAdvanced ? 'fa-minus-circle' : 'fa-plus-circle'"
              ></i>
            </a>
          </div>
          <div class="text-right nowrap" style="margin-left: 10px">
            <a
              href="javascript:void(0);"
              @click="toggleQuery"
              class="collapse-to-icon"
            >
              Query
              <i
                class="inline-icon-right fas"
                :class="[
                  showQuery || showEditQuery ? 'fa-eye-slash' : 'fa-eye',
                ]"
              ></i>
            </a>
          </div>
          <div class="text-right nowrap" style="margin-left: 10px">
            <a
              href="javascript:void(0);"
              @click="reset"
              class="collapse-to-icon"
            >
              Reset <i class="inline-icon-right fas fa-trash"></i>
            </a>
          </div>
          <div class="text-right nowrap" style="margin-left: 10px">
            <a
              href="javascript:void(0);"
              @click="showResources = !showResources"
              id="btnResources"
              class="collapse-to-icon"
            >
              Resources <i class="fas fa-list inline-icon-right"></i>
            </a>
          </div>
          <transition name="slidedown">
            <ResourceList
              v-if="showResources"
              v-dismiss="{ switch: 'showResources', ignore: ['#btnResources'] }"
            ></ResourceList>
          </transition>
        </div>
      </div>
      <transition name="slidedown">
        <div class="multisearch-advanced flex-container" v-if="showAdvanced">
          <FilterGroup
            filter-id="group_root"
            v-bind:nest-level="0"
            key="root"
          ></FilterGroup>
        </div>
      </transition>
      <Copyable
        :copy-text="JSON.stringify(requestBody)"
        v-if="showQuery"
        :edit-button="true"
        @edit="toggleEditQuery"
      >
        <pre>{{ requestBody(false) }}</pre>
      </Copyable>
      <Editable
        :edit-text="JSON.stringify(requestBody(false), null, 2)"
        v-if="showEditQuery"
        :edit-status="status.queryEdit"
        @save="saveQueryEdit"
        :long="true"
      />

      <Results @show-query="showQuery = true" @reset="reset"></Results>
    </div>
  </div>
</template>

<script>
import Loading from './components/Loading.vue';
import LoadError from './components/LoadError.vue';
import FilterGroup from './components/FilterGroup.vue';
import Results from './components/Results.vue';
import Copyable from './components/misc/Copyable.vue';
import Editable from './components/misc/Editable.vue';
import ImageViewer from './components/misc/ImageViewer.vue';
import { mapActions, mapMutations, mapState, mapGetters } from 'vuex';

const ResourceList = import('./components/ResourceList.vue');

export default {
  name: 'App',
  components: {
    Editable,
    ResourceList: () => ({
      component: ResourceList,
      loading: Loading,
      error: LoadError,
    }),
    Loading,
    LoadError,
    FilterGroup,
    Results,
    Copyable,
    ImageViewer,
  },
  data: function () {
    return {
      showResources: false,
      showAdvanced: true,
      showQuery: false,
      showEditQuery: false,
    };
  },
  computed: {
    ...mapGetters('appState', ['app']),
    ...mapState('appState', ['status']),
    ...mapGetters('results/query', ['requestBody']),
    ...mapState('results/query/resources', ['packageList', 'resourceIds']),
    ...mapState('results/display', ['showImage']),
    search: {
      get() {
        return this.$store.state.results.query.search;
      },
      set(value) {
        this.setSearch(value);
      },
    },
    watchedRequestBody() {
      return this.requestBody(false);
    },
  },
  created: function () {
    this.getPackageList().then(() => {
      this.getSchema().then(() => {
        if (this.$route.params !== undefined) {
          this.$store.dispatch('resolveUrl', this.$route);
        }
      });
    });

    this.getLicences();
  },
  methods: {
    ...mapMutations('results/query', ['setSearch']),
    ...mapMutations('results/query/resources', ['selectAllResources']),
    ...mapMutations('results/query/filters', ['resetFilters']),
    ...mapActions(['getSchema']),
    ...mapActions('results', ['runSearch', 'invalidate', 'reset']),
    ...mapActions('results/display', ['getLicences']),
    ...mapActions('results/query', ['setRequestBody']),
    ...mapActions('results/query/resources', ['getPackageList']),
    toggleQuery() {
      this.showQuery = !(this.showQuery || this.showEditQuery);
      this.showEditQuery = false;
    },
    toggleEditQuery() {
      this.showEditQuery = !this.showEditQuery;
      this.showQuery = !this.showEditQuery;
    },
    saveQueryEdit(editedQuery) {
      this.setRequestBody(JSON.parse(editedQuery))
        .then(() => {
          this.status.queryEdit.loading = false;
          this.status.queryEdit.failed = false;
          this.toggleEditQuery();
        })
        .catch((e) => {
          this.status.queryEdit.failed = true;
        });
    },
  },
  watch: {
    packageList: function (newList, oldList) {
      // if no resource ids are pre-selected,
      // select all resource ids once the package list loads
      if (oldList.length === 0 && this.resourceIds.length === 0) {
        this.selectAllResources();
      }
    },
    watchedRequestBody: {
      handler() {
        this.invalidate();
      },
      deep: true,
    },
  },
};
</script>

<template>
  <div class="filter-add">
    <span v-if="showText" class="filter-add-help-text">Add filters</span>
    <i
      class="fas fa-plus-square fa-lg"
      role="button"
      :aria-label="
        !showChoice ? 'Add a group or filter' : 'Close group or filter chooser'
      "
      @click="showChoice = !showChoice"
      :id="'show-choice-' + _uid"
    ></i>
    <transition name="slidedown">
      <div
        class="filter-add-choice floating"
        v-if="showChoice"
        v-dismiss="{ switch: 'showChoice', ignore: ['#show-choice-' + _uid] }"
      >
        <span
          v-if="canAddGroups"
          @click="newGroup"
          role="button"
          :id="'show-editor-groups-' + _uid"
          >new group</span
        >
        <div v-if="canAddTerms">
          <span
            @click="showEditor = true"
            role="button"
            :id="'show-editor-terms-' + _uid"
            >new term</span
          >
          <span
            @click="showPresets = true"
            role="button"
            :id="'show-editor-presets-' + _uid"
            >presets</span
          >
        </div>
      </div>
    </transition>
    <transition name="slideright">
      <TermEditor
        v-if="showEditor"
        :parent-id="parentId"
        v-dismiss="{
          switch: 'showEditor',
          ignore: [
            '#show-editor-groups-' + _uid,
            '#show-editor-terms-' + _uid,
            '.delete-field',
            '.term-editor-option',
          ],
        }"
      ></TermEditor>
    </transition>
    <transition name="slideright">
      <div
        v-if="showPresets"
        class="floating preset-picker"
        v-dismiss="{
          switch: 'showPresets',
          ignore: ['#show-editor-presets-' + _uid],
        }"
      >
        <select size="5">
          <option
            v-for="(presetName, presetKey) in presets"
            v-bind:key="presetKey"
            @dblclick="newPreset(presetKey)"
          >
            {{ presetName }}
          </option>
        </select>
      </div>
    </transition>
  </div>
</template>

<script>
import Loading from './Loading.vue';
import LoadError from './LoadError.vue';
import { mapGetters, mapActions } from 'vuex';

const TermEditor = import('./TermEditor.vue');

export default {
  name: 'FilterAdd',
  props: ['parentId', 'showText'],
  components: {
    TermEditor: () => ({
      component: TermEditor,
      loading: Loading,
      error: LoadError,
    }),
  },
  data: function () {
    return {
      showChoice: false,
      showEditor: false,
      showPresets: false,
    };
  },
  computed: {
    ...mapGetters('results/query/filters', ['getNestLevel', 'presets']),
    nestLevel() {
      return this.getNestLevel(this.parentId);
    },
    canAddGroups: function () {
      return this.nestLevel <= 1;
    },
    canAddTerms: function () {
      return true;
    },
  },
  methods: {
    ...mapActions('results/query/filters', ['addGroup', 'addPreset']),
    newGroup: function () {
      this.showChoice = false;
      this.addGroup({ parent: this.$parent.filterId });
    },
    newPreset(presetKey) {
      this.addPreset({ key: presetKey, parent: this.parentId });
      this.showPresets = false;
    },
  },
  watch: {
    showChoice(v) {
      if (v) {
        this.showEditor = false;
        this.showPresets = false;
      }
    },
    showEditor(v) {
      if (v) {
        this.showChoice = false;
        this.showPresets = false;
      }
    },
    showPresets(v) {
      if (v) {
        this.showChoice = false;
        this.showEditor = false;
      }
    },
  },
};
</script>

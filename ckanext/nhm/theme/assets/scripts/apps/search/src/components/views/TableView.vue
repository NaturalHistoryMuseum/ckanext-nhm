<template>
  <div class="table-view view-component" style="position: relative">
    <div class="scrolling-arrows">
      <div
        class="scroll-left"
        @click="tableScroll(-100)"
        :class="{ disabled: !scrollableLeft }"
      >
        <i class="fas fa-angle-double-left"></i>
      </div>
      <div
        class="scroll-right"
        @click="tableScroll(100)"
        :class="{ disabled: !scrollableRight }"
      >
        <i class="fas fa-angle-double-right"></i>
      </div>
    </div>
    <div
      class="table-grid"
      @resize="scrollable"
      ref="tableGrid"
      :style="{
        gridTemplateColumns:
          'repeat(4, max-content)' +
          (headers.length > 0 ? `repeat(${headers.length}, auto)` : ''),
      }"
    >
      <div class="th small-column"></div>
      <div class="th small-column">Dataset</div>
      <div class="th small-column">Resource</div>
      <div class="th small-column last-small-column">Record</div>
      <div
        class="th data-header"
        v-for="(headerGroup, index) in headers"
        :key="headerGroup.id"
      >
        <div>
          <span
            v-for="header in headerGroup"
            :key="header.id"
            class="term-group"
          >
            {{ header }}
          </span>
        </div>
        <div class="flex-container flex-nowrap flex-equal">
          <i
            class="delete-field fas fa-times-circle fa-xs"
            @click="removeHeader(index)"
          ></i>
          <i
            class="move-field fas fa-chevron-circle-left fa-xs"
            @click="moveHeader({ ix: index, by: -1 })"
            v-if="index > 0"
          ></i>
          <i
            class="move-field fas fa-chevron-circle-right fa-xs"
            @click="moveHeader({ ix: index, by: 1 })"
            v-if="index < headers.length - 1"
          ></i>
        </div>
      </div>

      <template v-for="(item, ix) in records">
        <div class="td small-column">{{ page * 100 + ix + 1 }}</div>
        <div class="td small-column">
          <a
            :href="resourceDetails[item.resource].packageUrl"
            :title="`View '${
              resourceDetails[item.resource].package_name
            }' dataset`"
          >
            {{ resourceDetails[item.resource].package_name }}
          </a>
        </div>
        <div class="td small-column">
          <a
            :href="resourceDetails[item.resource].resourceUrl"
            :title="`View '${resourceDetails[item.resource].name}' resource`"
          >
            {{ resourceDetails[item.resource].name }}
          </a>
        </div>
        <div class="td small-column">
          <a
            :href="`${resourceDetails[item.resource].resourceUrl}/record/${
              item.data._id
            }`"
            :title="`View record ${item.data._id}`"
          >
            <i class="fas fa-eye inline-icon-left"></i>View
          </a>
        </div>
        <div class="td" v-for="headerGroup in headers" :key="headerGroup.id">
          <span
            v-for="header in headerGroup"
            :key="header.id"
            class="term-group"
          >
            {{ getValue(item.data, header) || '--' }}
          </span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import BaseView from './BaseView.vue';

export default {
  extends: BaseView,
  name: 'TableView',
  data: function () {
    return {
      scrollableLeft: false,
      scrollableRight: false,
    };
  },
  computed: {
    tableGrid() {
      return $(this.$refs.tableGrid);
    },
  },
  methods: {
    tableScroll(amount) {
      this.tableGrid.scrollLeft(this.tableGrid.scrollLeft() + amount);
      this.scrollable();
    },
    scrollable() {
      if (this.$refs.tableGrid === undefined) {
        return;
      }
      this.scrollableLeft = this.tableGrid.scrollLeft() > 0;
      let fullWidth = this.$refs.tableGrid.scrollWidth;
      let viewWidth = Math.ceil(this.tableGrid.width());
      this.scrollableRight =
        fullWidth > viewWidth &&
        this.tableGrid.scrollLeft() < fullWidth - viewWidth;
    },
  },
  mounted() {
    // give the table a second to load properly...
    setTimeout(this.scrollable, 1000);
    $(window).resize(this.scrollable);
  },
  watch: {
    headers() {
      this.scrollable();
    },
  },
};
</script>

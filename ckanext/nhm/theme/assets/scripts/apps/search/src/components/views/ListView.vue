<template>
  <div class="flex-container flex-column flex-left full-width view-component">
    <div
      v-for="(item, index) in records"
      :key="item.id"
      class="record-item full-width"
    >
      <div class="record-header">
        <h4 class="record-name">
          <a
            :href="`${resourceDetails[item.resource].resourceUrl}/record/${
              item.data._id
            }`"
          >
            {{
              item.data[resourceDetails[item.resource].titleField] ||
              item.data._id
            }}
          </a>
        </h4>
        <span class="record-pkg">
          <i class="fas fa-archive inline-icon-left"></i>
          <a :href="resourceDetails[item.resource].packageUrl">
            {{ resourceDetails[item.resource].package_name }}
          </a>
        </span>
        <span class="indented record-res">
          ↳
          <i class="fas fa-list inline-icon-left"></i>
          <a :href="resourceDetails[item.resource].resourceUrl">
            {{ resourceDetails[item.resource].name }}
          </a>
        </span>
      </div>
      <div class="record-body flex-container flex-stretch-first flex-smallwrap">
        <ul class="list-unstyled">
          <li v-for="(headerGroup, index) in headers" :key="headerGroup.id">
            <span>
              <b
                v-for="header in headerGroup"
                :key="header.id"
                class="term-group"
              >
                {{ header }}
              </b>
            </span>
            <b>:</b>
            <span>
              <span
                v-for="header in headerGroup"
                :key="header.id"
                class="term-group"
              >
                {{ getValue(item.data, header) || '--' }}
              </span>
            </span>
          </li>
        </ul>
        <div class="tiny-grid">
          <img
            @click="showViewer(item, imgIx, index)"
            :src="imgRecord.image.thumb"
            :alt="imgRecord.image.preview"
            v-for="(imgRecord, imgIx) in getItemImages(item, false, index)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BaseView from './BaseView.vue';
import { mapGetters } from 'vuex';

export default {
  extends: BaseView,
  name: 'ListView',
  data: function () {
    return {
      showDetails: null,
    };
  },
  computed: {
    ...mapGetters('results/images', ['getItemImages']),
  },
  methods: {
    showViewer(record, imgIndex, recordIndex) {
      this.addPageImages(this.getItemImages(record, false, recordIndex));
      this.setViewerImage(imgIndex);
    },
  },
};
</script>

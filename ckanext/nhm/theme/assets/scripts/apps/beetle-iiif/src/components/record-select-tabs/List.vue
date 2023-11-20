<template>
  <div
    class="record-select-view biiif-list-track-container"
    ref="track"
    @scroll="onScroll"
  >
    <table class="table table-striped table-chunky">
      <thead>
        <tr>
          <th v-for="k in columnNames">
            {{ k }}
          </th>
          <th>Image</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(record, index) in records"
          :key="record.data._id"
          :data-item-index="index"
        >
          <td v-for="k in columnNames">{{ record.data[k] }}</td>
          <td @click="goto(index)">
            <img
              class="biiif-thumbnail-image"
              :style="{ height: `${thumbnailSize}px` }"
              :src="getRecordThumbnail(record)"
              :height="`${thumbnailSize}px`"
              draggable="false"
              :alt="`Thumbnail of ${record.data['Barcode']} from ${record.data['Collection Name']}`"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Base from './Base.vue';
import { mapGetters } from 'vuex';

export default {
  name: 'List',
  extends: Base,
  computed: {
    ...mapGetters(['columnNames']),
  },
};
</script>

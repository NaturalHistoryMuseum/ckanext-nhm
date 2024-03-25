<template>
  <div :class="$style.list" ref="listContainer">
    <div
      :class="$style.item"
      v-for="record in store.allRecords"
      :key="record.id"
    >
      <div :class="$style.header">
        <span :class="$style.title">{{ record.title }}</span>
        <span :class="$style.subtitle">{{ record.subtitle }}</span>
      </div>
      <div :class="$style.body">
        <div :class="$style.data">
          <dl>
            <template v-for="item in record.dataSummary">
              <dt>{{ item.key }}</dt>
              <dd>{{ item.value }}</dd>
            </template>
          </dl>
        </div>
        <div
          :class="[
            $style.tinyGallery,
            record.images && record.images.length > 1 ? $style.multiImg : '',
          ]"
        >
          <img
            v-for="img in record.images"
            :src="img.thumbnail"
            :alt="record.title"
            @click="store.changeImage(img)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useStore } from '../../store';
import { ref } from 'vue';
import { useInfiniteScroll } from '@vueuse/core';

const store = useStore();
const listContainer = ref(null);

useInfiniteScroll(
  listContainer,
  () => {
    if (
      listContainer.value &&
      store.more &&
      !store.pending &&
      !store.disableAutoLoad
    ) {
      store.getRecords();
    }
  },
  { distance: 50, interval: 1000 },
);
</script>

<style module lang="scss">
.list {
  min-height: 300px;
  max-height: 600px;
  overflow-y: scroll;
}

.item {
  margin-bottom: 1em;
  border-top: 1px solid #9a9a9a;
  border-bottom: 1px solid #9a9a9a;
}

.body {
  display: grid;
  grid-template-columns: 1fr 200px;
  gap: 1em;
  padding: 5px;
}

.data {
  & > dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.2em 1em;

    & > dt {
      grid-column: 1;
    }
    & > dd {
      grid-column: 2;
    }
  }
}

.header {
  background-color: #f3f3f3;
  padding: 5px;
}

.title {
  font-size: 1.5em;
  display: block;
  font-family: var(--zoa-header-font, sans-serif);
  font-weight: bold;
}

.subtitle {
  font-size: 1.2em;
  display: block;
}

.tinyGallery {
  display: grid;
  gap: 4px;
  width: 200px;

  &.multiImg {
    grid-template-columns: 1fr 1fr;
  }
}
</style>

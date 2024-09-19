<template>
  <div :class="$style.gallery" ref="galleryContainer">
    <div
      :class="$style.tile"
      v-for="img in store.allImages"
      :style="{ gridRowEnd: `span ${imageHeight(img)}` }"
      role="button"
      :key="img.id"
    >
      <img
        :src="img.thumbnail"
        :alt="img.record.title"
        @click="store.changeImage(img)"
        :class="$style.thumbnailImage"
      />
      <div :class="$style.thumbnailLabel">
        <div :class="$style.thumbnailLabelTitle">
          {{ img.record.title }}
        </div>
        <div :class="$style.thumbnailLabelSubtitle" v-if="img.record.subtitle">
          {{ img.record.subtitle }}
        </div>
      </div>
    </div>
  </div>
  <div
    :class="$style.loadMore"
    v-if="store.more && !store.pending"
    @click="store.getRecords()"
  >
    <span><b>Load more...</b></span>
  </div>
</template>

<script setup>
import { useStore } from '../../store';
import { onMounted, ref } from 'vue';
import { useInfiniteScroll, useResizeObserver } from '@vueuse/core';
import { debounce } from 'dettle';

const store = useStore();
const galleryContainer = ref(null);

// image sizing
const colWidth = ref(0);
const minImgWidth = 200;
const gridGap = 10;

useInfiniteScroll(
  galleryContainer,
  () => {
    if (
      galleryContainer.value &&
      store.more &&
      !store.pending &&
      !store.disableAutoLoad
    ) {
      // if the container element does not exist (e.g. because it's just reloading) it tries to scroll forever
      store.getRecords();
    }
  },
  { distance: 50, interval: 1000 },
);

function imageHeight(imageRecord) {
  const height =
    colWidth.value / (imageRecord.iiifData.width / imageRecord.iiifData.height);
  const rowHeight = (height + gridGap) / gridGap;
  return Math.ceil(rowHeight);
}

function setColWidth() {
  let currentWidth = 0;
  try {
    currentWidth = galleryContainer.value.clientWidth;
  } catch {
    //
  }
  if (currentWidth === 0) {
    // the container is about 88% of the full window width; this is here just in
    // case the container hasn't loaded yet
    currentWidth = window.innerWidth * 0.88;
  }

  let cols = 0;
  let w = 0;
  while (true) {
    w += minImgWidth;
    if (w > currentWidth) {
      break;
    }
    cols++;
    if (w + gridGap + minImgWidth > currentWidth) {
      break;
    }
    w += gridGap;
  }

  colWidth.value = Math.ceil(currentWidth / cols) - gridGap;
}

onMounted(() => {
  setTimeout(setColWidth, 500);
});
useResizeObserver(galleryContainer, debounce(setColWidth, 200));
</script>

<style module lang="scss">
.gallery {
  display: grid;
  grid-gap: 10px;
  grid-template-columns: repeat(
    auto-fill,
    minmax(200px, 1fr)
  ); // also change above and in models.js
  grid-auto-rows: 0;
  min-height: 300px;
  max-height: 600px;
  overflow-y: scroll;
  overflow-x: hidden;
  padding: 10px;

  & .tile {
    grid-row-end: span 10; // default
    width: 100%;
    position: relative;
    -o-transition: 0.2s;
    -ms-transition: 0.2s;
    -moz-transition: 0.2s;
    -webkit-transition: 0.2s;
    transition: 0.2s;

    & > .thumbnailImage {
      width: 100% !important;
      height: 100% !important; // this squishes/stretches the image very slightly but it makes the layout look better
    }

    &:hover {
      transform: scale(1.1);
      z-index: 100;
    }

    & .thumbnailLabel {
      position: absolute;
      bottom: 0;
      left: 0;
      padding: 2px 5px 5px;
      background: #ffffffaa;
      text-align: center;
      width: 100%;
      font-size: 14px;

      & > * {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
      }

      & .thumbnailLabelTitle {
        font-weight: bold;
      }
      & .thumbnailLabelSubtitle {
        font-style: italic;
        font-size: 0.9em;
      }
    }
  }
}

.loadMore {
  width: 100%;
  padding: 1em;
  display: flex;
  justify-content: center;

  & > span {
    cursor: pointer;
    padding: 10px 20px;
    background: #eee;
    border-radius: 10px;
  }
}
</style>

<template>
  <div
    :class="[$style.overlay, $style.main]"
    :style="{ top: showOverlay ? '20%' : '100%' }"
    ref="container"
  >
    <zoa-button size="sm" @click="showOverlay = false" :class="$style.close"
      >close
    </zoa-button>
    <Viewer v-show="showOverlay" />
    <div
      :class="$style.record"
      v-if="showOverlay && (currentRecord || currentImage)"
    >
      <div :class="$style.header">
        <h2 :class="$style.title">
          {{ currentRecord ? currentRecord.title : currentImage.name }}
        </h2>
        <template v-if="currentRecord">
          <span :class="$style.subtitle">{{ currentRecord.subtitle }}</span>
          <div :class="$style.recordLinks">
            <a
              :href="currentRecord.url"
              :class="$style.recordLink"
              v-if="currentRecord && currentRecord.url"
              >View record</a
            >
            <form method="get" :action="`${currentImage.url}/original`">
              <zoa-button size="sm">
                <i class="fas fa-download" />
                <span class="sr-only">Download image</span>
              </zoa-button>
            </form>
            <zoa-modal header="Sharing links" :button-args="{ size: 'sm' }">
              <template v-slot:button>
                <i class="fas fa-share-alt" />
                <span class="sr-only">Share</span>
              </template>
              <div :class="$style.shareLinks">
                <span>Record</span>
                <Copyable v-model="shareUrlRecord">
                  <a :href="currentRecord.imageViewerUrl">{{
                    shareUrlRecord
                  }}</a>
                </Copyable>
                <span>Image</span>
                <Copyable v-model="shareUrlImage">
                  <a :href="currentImage.imageViewerUrl">{{ shareUrlImage }}</a>
                </Copyable>
              </div>
            </zoa-modal>
            <a
              target="_blank"
              :href="currentRecord.manifest"
              :class="$style.manifestBtn"
            >
              <img src="/images/iiif.png" alt="IIIF Manifest" />
            </a>
          </div>
        </template>
      </div>
      <div :class="$style.fieldToggle">
        <zoa-input
          zoa-type="checkbox"
          v-model="useOriginalLabels"
          label="Use original field names"
          label-position="left"
        />
      </div>
      <div v-if="currentRecord" :class="$style.dataBlock">
        <h3>Record</h3>
        <dl>
          <template v-for="item in currentRecord.displayData">
            <dt>{{ useOriginalLabels ? item.key : sentenceCase(item.key) }}</dt>
            <dd>{{ item.value }}</dd>
          </template>
        </dl>
      </div>
      <div v-if="currentImage" :class="$style.dataBlock">
        <h3>Image</h3>
        <dl>
          <dt>URL</dt>
          <dd>
            <a :href="currentImage.url">{{ currentImage.url }}</a>
          </dd>
          <template v-for="item in currentImage.displayData">
            <dt>{{ useOriginalLabels ? item.key : sentenceCase(item.key) }}</dt>
            <dd>
              <a
                :href="item.value"
                v-if="item.value.toString().startsWith('http')"
                >{{ item.value }}</a
              >
              <template v-else>{{ item.value }}</template>
            </dd>
          </template>
        </dl>
      </div>
    </div>
  </div>
  <div v-if="showClosed" :class="[$style.overlay, $style.closed]">
    <zoa-button size="sm" @click="showOverlay = true" :class="$style.open"
      >open viewer
    </zoa-button>
  </div>
</template>

<script setup>
import Viewer from './Viewer.vue';
import { useStore } from '../store';
import { ZoaButton, ZoaInput, ZoaModal } from '@nhm-data/zoa';
import { ref, watch, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { sentenceCase } from 'change-case';
import { onClickOutside } from '@vueuse/core';
import Copyable from './elements/Copyable.vue';

const store = useStore();
const { showOverlay, currentRecord, currentImage } = storeToRefs(store);

const showClosed = ref(true);
const useOriginalLabels = ref(false);
const container = ref(null);

const shareUrlRecord = computed(() =>
  fullUrl(currentRecord.value ? currentRecord.value.imageViewerUrl : ''),
);
const shareUrlImage = computed(() =>
  fullUrl(currentImage.value ? currentImage.value.imageViewerUrl : ''),
);

function fullUrl(partialUrl) {
  return [window.location.origin, partialUrl].join('');
}

onClickOutside(container, () => {
  if (showOverlay.value) {
    // only close. do not open
    showOverlay.value = false;
  }
});

watch(showOverlay, () => {
  if (showOverlay.value) {
    showClosed.value = false;
  } else {
    // delay showing the closed bar a little
    setTimeout(() => {
      showClosed.value = true;
    }, 350);
  }
});
</script>

<style module lang="scss">
.overlay {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #ffffffee;
  border-top: 2px solid #9a9a9a;
  display: grid;

  & h3 {
    margin-bottom: 0.5em;
  }
}

.main {
  padding: 0.5em 1em 1em;
  z-index: 9999;
  grid-template-columns: 70% 1fr;
  grid-template-rows: auto 1fr;
  gap: 5px 1em;

  overflow-y: hidden;
  transition: all 400ms ease-in;

  & > .close {
    grid-column: span 2;
    justify-self: end;
  }
}

.closed {
  padding: 0.5em 1em;
  z-index: 9998;
  justify-items: end;
  top: auto;
}

.record {
  padding: 1em;
  max-height: 100%;
  overflow-y: scroll;

  & dd {
    margin-bottom: 0.5em;
  }

  & .header {
    display: grid;
    gap: 2px;
    position: relative;

    & .title {
      font-size: 2em;
    }

    & .subtitle {
      font-size: 1.2em;
    }
  }

  & .fieldToggle {
    padding: 1em 0;
    display: flex;
    justify-content: center;

    & label {
      margin-bottom: 0;
    }
  }
}

.recordLinks {
  display: flex;
  gap: 1em;
  align-items: center;

  .recordLink {
    flex-grow: 1;
  }

  .shareBtn {
    cursor: pointer;
  }

  .manifestBtn img {
    height: 1.5em;
  }
}

.shareLinks {
  display: grid;

  & span:not(:first-child) {
    margin-top: 10px;
  }
}

.dataBlock {
  &:not(:last-child) {
    margin-bottom: 1em;
    padding-bottom: 1em;
    border-bottom: 1px solid #9a9a9a;
  }
}
</style>

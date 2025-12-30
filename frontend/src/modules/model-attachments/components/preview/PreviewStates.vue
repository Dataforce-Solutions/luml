<template>
  <div class="preview-state">
    <div v-if="state === 'empty'" class="state-content empty">
      <span>File is empty</span>
    </div>

    <div v-else-if="state === 'too-big'" class="state-content warning">
      <span>File is too large for preview</span>
    </div>

    <div v-else-if="state === 'unsupported'" class="state-content warning">
      <span>This file type is not supported for preview</span>
    </div>

    <div v-else-if="state === 'error'" class="state-content error">
      <span>{{ errorMessage || 'Failed to load preview' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PreviewStatesProps } from '../../interfaces/interfaces'

defineProps<PreviewStatesProps>()
</script>

<style scoped>
.preview-state {
  flex: 1;
  display: flex;
  height: 100%;
}

.state-text {
  display: left;
  color: var(--p-form-field-float-label-color);
}


.icon {
  flex: 0 0 auto;
  color: var(--p-text-link-color);
}

.icon.error {
  color: var(--p-badge-danger-background);
}

.title {
  font-size: 16px;
  font-weight: 500;
  color: var(--p-form-field-float-label-color);
}
</style>

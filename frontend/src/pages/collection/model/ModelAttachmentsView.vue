<template>
  <div v-if="isInitializing || loading">
    <UiPageLoader></UiPageLoader>
  </div>

  <AttachmentsView
    v-else-if="tree.length"
    :tree="tree"
    :selected-file="selectedFile"
    :attachments-index="attachmentsIndex"
    :tar-base-offset="tarBaseOffset"
    :download-url="downloadUrl"
    @select="selectFile"
  />

  <div v-else-if="error" class="error-state">
    <p>{{ error }}</p>
  </div>

  <div v-else class="empty-state">
    <p>This attachment is empty.</p>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useModelsStore } from '@/stores/models'
import { ModelDownloader } from '@/lib/bucket-service'
import { AttachmentsView, useModelAttachments } from '@/modules/model-attachments'
import UiPageLoader from '@/components/ui/UiPageLoader.vue'

const route = useRoute()
const modelsStore = useModelsStore()

const {
  tree,
  selectedFile,
  attachmentsIndex,
  tarBaseOffset,
  downloadUrl,
  loading,
  error,
  init,
  selectFile,
  reset,
} = useModelAttachments()

const isInitializing = ref(true)

const currentModel = computed(() => {
  if (typeof route.params.modelId !== 'string') return undefined
  return modelsStore.modelsList.find((model) => model.id === route.params.modelId)
})

onMounted(async () => {
  const model = currentModel.value
  if (!model?.file_index) {
    isInitializing.value = false
    return
  }

  try {
    const url = await modelsStore.getDownloadUrl(model.id)
    const downloader = new ModelDownloader(url)

    await init(downloader, model)
  } catch (e) {
    console.error(e)
  } finally {
    isInitializing.value = false
  }
})

onUnmounted(() => {
  reset()
})
</script>
<style scoped>
.attachments-wrapper {
  display: flex;
  gap: 16px;
  height: calc(100vh - 320px);
}
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--p-form-field-float-label-color);
}
</style>

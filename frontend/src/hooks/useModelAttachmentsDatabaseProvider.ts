import { ref } from 'vue'
import {
  ModelAttachmentsDatabaseProvider,
  type ModelAttachmentsProviderConfig,
} from '../modules/model-attachments/models/ModelAttachmentsDatabaseProvider'

export function useModelAttachmentsDatabaseProvider() {
  const provider = ref<ModelAttachmentsDatabaseProvider | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function init(config: ModelAttachmentsProviderConfig): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const newProvider = new ModelAttachmentsDatabaseProvider(config)
      await newProvider.init()
      provider.value = newProvider
    } catch (e) {
      console.error('Failed to initialize attachments provider:', e)
      error.value = e instanceof Error ? e.message : 'Unknown error'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    provider,
    loading,
    error,
    init,
  }
}

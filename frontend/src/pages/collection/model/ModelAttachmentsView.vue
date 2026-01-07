<template>
  <UiPageLoader v-if="loading" />
  <ModelAttachments v-if="provider" :provider="provider" />
</template>
<script setup lang="ts">
import type { MlModel } from '@/lib/api/orbit-ml-models/interfaces'
import { ModelAttachments } from '@/modules/model-attachments'
import { onMounted } from 'vue'
import { useModelsStore } from '@/stores/models'
import { useModelAttachmentsDatabaseProvider } from '@/hooks/useModelAttachmentsDatabaseProvider'
import { ModelDownloader } from '@/lib/bucket-service'
import { FnnxService } from '@/lib/fnnx/FnnxService'

type Props = {
  model?: MlModel
}

const props = defineProps<Props>()

const modelsStore = useModelsStore()
const { provider, loading, init } = useModelAttachmentsDatabaseProvider()

onMounted(async () => {
  if (provider.value) return

  try {
    if (!props.model) throw new Error('Current model does not exist')

    const url = await modelsStore.getDownloadUrl(props.model.id)
    const downloader = new ModelDownloader(url)

    await init({
      downloader,
      model: props.model,
      findAttachmentsTarPath: (fileIndex) => FnnxService.findAttachmentsTarPath(fileIndex),
      findAttachmentsIndexPath: (fileIndex) => FnnxService.findAttachmentsIndexPath(fileIndex),
    })
  } catch (e) {
    console.error(e)
  }
})
</script>
<style scoped></style>

<template>
  <div v-if="loading">
    <Skeleton style="height: 210px; margin-bottom: 20px"></Skeleton>
    <div
      style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px"
    >
      <Skeleton style="height: 300px; width: 100%"></Skeleton>
      <Skeleton style="height: 300px; width: 100%"></Skeleton>
    </div>
    <Skeleton style="height: 210px; margin-bottom: 20px"></Skeleton>
  </div>
  <ExperimentSnapshot
    v-if="modelsStore.experimentSnapshotProvider && model"
    :provider="modelsStore.experimentSnapshotProvider"
    :models-ids="[String(model.id)]"
    :models-info="modelsInfo"
  ></ExperimentSnapshot>
</template>

<script setup lang="ts">
import type { ModelInfo } from '@/modules/experiment-snapshot/interfaces/interfaces'
import type { MlModel } from '@/lib/api/orbit-ml-models/interfaces'
import { ExperimentSnapshot } from '@/modules/experiment-snapshot'
import { computed, onMounted, ref } from 'vue'
import { useModelsStore } from '@/stores/models'
import { Skeleton } from 'primevue'
import { useExperimentSnapshotsDatabaseProvider } from '@/hooks/useExperimentSnapshotsDatabaseProvider'
import { getModelColorByIndex } from '@/modules/experiment-snapshot/helpers/helpers'

type Props = {
  model?: MlModel
}

const props = defineProps<Props>()

const modelsStore = useModelsStore()
const { init } = useExperimentSnapshotsDatabaseProvider()

const loading = ref(false)

const modelsInfo = computed(() => {
  const data: Record<string, ModelInfo> = {}
  if (props.model) {
    data[props.model.id] = {
      name: props.model.model_name,
      color: getModelColorByIndex(0),
    }
  }
  return data
})

onMounted(async () => {
  if (modelsStore.experimentSnapshotProvider) return
  try {
    loading.value = true
    if (!props.model) throw new Error('Current model does not exist')
    await init([props.model])
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped></style>

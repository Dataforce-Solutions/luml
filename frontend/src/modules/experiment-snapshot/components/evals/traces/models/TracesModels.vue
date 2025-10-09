<template>
  <div class="models">
    <TracesModel
      v-for="item in uniqueModelsIds"
      :key="item"
      :id="item"
      :name="modelsInfo[item]?.name"
    ></TracesModel>
  </div>
</template>

<script setup lang="ts">
import { useEvalsStore } from '@/modules/experiment-snapshot/store/evals'
import TracesModel from './TracesModel.vue'
import { computed } from 'vue'
import type { ModelsInfo } from '@/modules/experiment-snapshot/interfaces/interfaces'

type Props = {
  modelsInfo: ModelsInfo
}

defineProps<Props>()

const evalsStore = useEvalsStore()

const uniqueModelsIds = computed(() => {
  if (!evalsStore.currentEvalData) return []
  const idsSet = evalsStore.currentEvalData.reduce((acc, item) => {
    acc.add(item.modelId)
    return acc
  }, new Set<string>())
  return Array.from(idsSet)
})
</script>

<style scoped>
.models {
  display: flex;
}
</style>

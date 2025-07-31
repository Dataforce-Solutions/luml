<template>
  <div v-if="isTabular" class="model-info">
    <ModelPerformance
      :total-score="getTotalScore"
      :test-metrics="testMetrics"
      :training-metrics="testMetrics"
      :task="Tasks.TABULAR_CLASSIFICATION"
      grid-metrics
    ></ModelPerformance>
    <div class="features card">
      <header class="card-header">
        <h3 class="card-title">Top {{ 5 }} features</h3>
        <info
          width="20"
          height="20"
          class="info-icon"
          v-tooltip.bottom="
            `Understand which features play the biggest role in your model's outcomes to guide further data analysis`
          "
        />
      </header>
      <div>{{ currentModel?.manifest.producer_tags }}</div>
    </div>
  </div>
  <div v-else class="card">
    <header class="card-header">
      <h3 class="card-title card-title--medium">Inputs and outputs</h3>
    </header>
    <div>{{ currentModel?.manifest.producer_tags }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useModelsStore } from '@/stores/models'
import { useRoute } from 'vue-router'
import { getMetrics, toPercent } from '@/helpers/helpers'
import { Tasks } from '@/lib/data-processing/interfaces'
import ModelPerformance from '@/components/model/ModelPerformance.vue'
import { Info } from 'lucide-vue-next'

const modelsStore = useModelsStore()
const route = useRoute()

const currentModel = computed(() => {
  if (typeof route.params.modelId !== 'string') return undefined
  return modelsStore.modelsList.find((model) => model.id === +route.params.modelId)
})
const isTabular = computed(() => !currentModel.value)
const testMetrics = computed(() => {
  if (!currentModel.value) return []
  const testMetrics: any = currentModel.value.metrics
  return getMetrics(
    { test_metrics: testMetrics, train_metrics: testMetrics },
    Tasks.TABULAR_CLASSIFICATION,
    'test_metrics',
  )
})
const getTotalScore = computed(() =>
  currentModel.value ? toPercent(+currentModel.value.metrics.SC_SCORE) : 0,
)
// const getTop5Feature = computed(
//   () => currentModel.value?.importances.filter((item, index) => index < 5) || [],
// )
</script>

<style scoped>
.model-info {
  display: grid;
  grid-template-columns: 55% 1fr;
  gap: 20px;
  align-items: flex-start;
}

.card {
  padding: 24px;
  border: 1px solid var(--p-content-border-color);
  background-color: var(--p-card-background);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 20px;
}

.card-title--medium {
  font-weight: 500;
}

.info-icon {
  color: var(--p-icon-muted-color);
}
</style>

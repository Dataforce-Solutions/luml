<template>
  <DynamicMetricsItemContent :title="metricName" class="chart-wrapper" @scale="setScaledChart">
    <div ref="chartRef" style="height: 200px; width: 100%"></div>
    <template #scaled>
      <div ref="chartScaledRef" style="height: calc(100vh - 100px); width: 100%"></div>
    </template>
  </DynamicMetricsItemContent>
</template>

<script setup lang="ts">
import type { ExperimentSnapshotDynamicMetric, ModelInfo } from '../../interfaces/interfaces'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import DynamicMetricsItemContent from './DynamicMetricsItemContent.vue'
import { useVariableValue } from '../../hooks/useVariableValue'
import { plotlyLineChartLayout } from '../../lib/plotly/layouts'
import { cutStringOnMiddle } from '@/modules/experiment-snapshot/helpers/helpers'
import { useThemeStore } from '@/stores/theme'

const { getVariablesValues } = useVariableValue()
const themeStore = useThemeStore()

type Props = {
  metricName: string
  data: ExperimentSnapshotDynamicMetric[]
  modelsInfo: Record<string, ModelInfo>
}

const props = defineProps<Props>()

const chartRef = ref<HTMLDivElement | null>(null)
const chartScaledRef = ref<HTMLDivElement | null>(null)

const plotlyData = computed(() => {
  const data: ExperimentSnapshotDynamicMetric[] = JSON.parse(JSON.stringify(props.data))
  return data
    .filter((item) => item.modelId)
    .map((item) => {
      const color = getVariablesValues([props.modelsInfo[item.modelId]?.color])[0]
      const modelName = getFormattedName(props.modelsInfo[item.modelId]?.name)
      return {
        ...item,
        type: 'scatter',
        mode: item.x.length > 1 ? 'lines' : 'markers',
        name: props.metricName,
        line: { color: color, width: 2, shape: 'spline', smoothing: 1.2 },
        hovertemplate: '<b>Value:</b> %{y}<br>' + `<b>Model:</b> ${modelName}<extra></extra>`,
      }
    })
})

function setScaledChart() {
  nextTick(() => {
    const layout = getPlotlyLayout()
    Plotly.newPlot(chartScaledRef.value, plotlyData.value, layout, {
      displayModeBar: false,
      responsive: true,
    })
  })
}

function getFormattedName(name: string | undefined) {
  if (!name) return ''
  if (name.length > 24) {
    return cutStringOnMiddle(name, 24)
  }
  return name
}

function getPlotlyLayout() {
  const [bgColor, borderColor, textColor, gridColor] = getVariablesValues([
    'var(--p-card-background)',
    'var(--p-content-border-color)',
    'var(--p-text-muted-color)',
    'var(--p-datatable-row-background)',
  ])

  return plotlyLineChartLayout({
    title: props.metricName,
    bgColor,
    borderColor,
    textColor,
    gridColor,
  })
}

watch(
  () => themeStore.getCurrentTheme,
  () => {
    const layout = getPlotlyLayout()
    Plotly.relayout(chartRef.value, layout)
  },
)

onMounted(() => {
  const layout = getPlotlyLayout()
  Plotly.newPlot(chartRef.value, plotlyData.value, layout, {
    displayModeBar: false,
    responsive: true,
  })
})
</script>

<style scoped>
.charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-wrapper {
  height: 300px;
}
</style>

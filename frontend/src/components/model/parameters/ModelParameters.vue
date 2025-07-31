<template>
  <div>
    <UiCard title="Model parameters">
      <template #header-right>
        <Button severity="secondary" variant="text" @click="scaled = true">
          <template #icon>
            <Maximize2 :size="14" />
          </template>
        </Button>
      </template>
      <UiScalable v-model="scaled" title="Model parameters">
        <ModelParametersList :parameters="parametersInCard"></ModelParametersList>
        <template #scaled>
          <ModelParametersList :parameters="parameters"></ModelParametersList>
        </template>
      </UiScalable>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Button } from 'primevue'
import { Maximize2 } from 'lucide-vue-next'
import UiCard from '@/components/ui/UiCard.vue'
import UiScalable from '@/components/ui/UiScalable.vue'
import ModelParametersList from './ModelParametersList.vue'

const scaled = ref(false)

const parameters = ref({
  random_state: 42,
  solver: 'liblinear',
  C: 0.5,
  class_weight: 'None',
  penalty: 'Above average mid-training loss, but improves towards the end',
})

const parametersInCard = computed(() => {
  const entries = Object.entries(parameters.value).filter((item, index) => index < 5)
  return Object.fromEntries(entries)
})
</script>

<style scoped></style>

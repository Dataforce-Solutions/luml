<template>
  <Breadcrumb :model="breadcrumbs" :pt="{ root: { style: 'padding-left: 0' } }">
    <template #item="{ item, props }">
      <RouterLink v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
        <a :href="href" v-bind="props.action" @click="navigate">
          {{ item.label }}
        </a>
      </RouterLink>
    </template>
  </Breadcrumb>
</template>

<script setup lang="ts">
import type { MenuItem } from 'primevue/menuitem'
import { Breadcrumb } from 'primevue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCollectionsStore } from '@/stores/collections'
import { useModelsStore } from '@/stores/models'

const route = useRoute()
const collectionStore = useCollectionsStore()
const modelsStore = useModelsStore()

const breadcrumbs = computed<(MenuItem & { route: string })[]>(() => {
  const list = [
    {
      label: 'Registry',
      route: `/organization/${route.params.organizationId}/orbit/${route.params.id}`,
    },
  ]
  if (collectionStore.currentCollection) {
    list.push({
      label: collectionStore.currentCollection.name,
      route: `/organization/${route.params.organizationId}/orbit/${route.params.id}/collection/${route.params.collectionId}`,
    })
  }
  const model = modelsStore.modelsList.find((model) => model.id === +route.params.modelId)
  if (model) {
    list.push({
      label: model.model_name,
      route: `/organization/${route.params.organizationId}/orbit/${route.params.id}/collection/${route.params.collectionId}/models/${route.params.modelId}`,
    })
  }

  return list
})
</script>

<style scoped></style>

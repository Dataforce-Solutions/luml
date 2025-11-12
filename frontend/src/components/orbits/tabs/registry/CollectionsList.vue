<template>
  <div class="list-container">
    <IconField>
      <InputText v-model="searchQuery" size="small" placeholder="Search" />
      <InputIcon>
        <Search :size="12" />
      </InputIcon>
    </IconField>

    <div class="list">
      <CollectionCard
        v-for="collection in filteredCollections"
        :key="collection.id"
        :edit-available="editAvailable"
        :data="collection"
      ></CollectionCard>

      <div v-if="filteredCollections.length === 0" class="no-results">Collections not found...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCollectionsStore } from '@/stores/collections'
import CollectionCard from './CollectionCard.vue'
import { IconField, InputIcon, InputText } from 'primevue'
import { Search } from 'lucide-vue-next'

type Props = {
  editAvailable: boolean
}

defineProps<Props>()

const collectionsStore = useCollectionsStore()
const searchQuery = ref('')

const filteredCollections = computed(() => {
  if (!searchQuery.value.trim()) {
    return collectionsStore.collectionsList
  }

  const query = searchQuery.value.toLowerCase().trim()

  return collectionsStore.collectionsList.filter((collection) => {
    const matchesName = collection.name?.toLowerCase().includes(query)
    const matchesTags = collection.tags?.some((tag: string) => tag.toLowerCase().includes(query))

    return matchesName || matchesTags
  })
})
</script>

<style scoped>
.list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

:deep(.p-iconfield) {
  max-width: 250px;
}

:deep(.p-iconfield .p-inputicon:last-child) {
  inset-inline-end: 21px;
}

:deep(.p-iconfield .p-inputtext) {
  width: 100%;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.no-results {
  text-align: center;
  padding: 40px;
  color: var(--p-text-muted-color);
  font-size: 14px;
}
</style>

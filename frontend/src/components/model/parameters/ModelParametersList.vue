<template>
  <ul class="parameters__list">
    <li v-for="[key, value] of Object.entries(parameters)" class="parameters__item parameter">
      <div class="parameter__label">{{ key }}</div>
      <div class="parameter__value">{{ value }}</div>
    </li>
  </ul>
</template>

<script setup lang="ts">
type Props = {
  parameters: Record<string, string | number>
}

defineProps<Props>()
</script>

<style scoped>
.parameters__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.parameter {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 24px;
  font-size: 14px;
}
.parameter__label {
  color: var(--p-text-muted-color);
}
</style>

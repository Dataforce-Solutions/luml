<template>
  <Toast position="top-right">
    <template #message="slotProps">
      <Check class="p-toast-message-icon" v-if="slotProps.message.severity === 'success'" />
      <div class="p-toast-message-text">
        <span class="p-toast-summary">{{ slotProps.message.summary }}</span>
        <div
          class="p-toast-detail"
          v-html="sanitizeDetail(slotProps.message.detail)"
          @click="handleLinkClick"
        ></div>
      </div>
    </template>
  </Toast>
</template>

<script setup lang="ts">
import Toast from 'primevue/toast'
import { useRouter } from 'vue-router'
import { Check } from 'lucide-vue-next'
import DOMPurify from 'dompurify'

const router = useRouter()

function sanitizeDetail(detail: string) {
  return DOMPurify.sanitize(detail)
}

function handleLinkClick(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (target.classList.contains('toast-action-link')) {
    event.preventDefault()
    const routeName = target.getAttribute('data-route')
    const routeParams = target.getAttribute('data-params')
    if (routeName) {
      router.push({
        name: routeName,
        params: routeParams ? JSON.parse(routeParams) : {},
      })
    }
  }
}
</script>

<style scoped>
:deep(.p-toast-detail a.toast-action-link) {
  display: inline-block;
  margin-top: 0.6rem;
  text-decoration: underline;
  cursor: pointer;
}
</style>

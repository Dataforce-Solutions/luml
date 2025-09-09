<template>
  <Dialog
    :visible="props.visible"
    @update:visible="emit('update:visible', $event)"
    position="topright"
    :draggable="false"
    style="margin-top: 80px; height: 86%; width: 420px"
    :pt="dialogPt"
  >
    <template #header>
      <h2 class="dialog-title">
        <Bolt :size="20" color="var(--p-primary-color)" />
        <span>Secret settings</span>
      </h2>
    </template>

    <Form id="secret-edit-form"
      class="form"
      :resolver="secretResolver"
      validateOnSubmit
      @submit="onComponentSubmit"
    >
      <div class="form-item">
        <label for="editSecretName" class="label">Name</label>
        <InputText
          v-model="formState.name"
          id="editSecretName"
          name="name"
          autofocus
        />
      </div>

      <div class="form-item">
        <label for="editSecretValue" class="label">Key</label>
        <Password
          v-model="formState.value"
          id="editSecretValue"
          name="value"
          :feedback="false"
          toggleMask
          fluid
          :key="secret?.id"
        />
      </div>

      <div class="form-item">
        <label for="tags" class="label">Tags</label>
        <AutoComplete
          v-model="formState.tags"
          id="tags"
          name="tags"
          :suggestions="autocompleteItems"
          @complete="searchTags"
          multiple
          fluid
        />
      </div>
    </Form>

    <template #footer>
      <div>
        <Button outlined severity="warn" @click="onComponentDelete">
          delete key
        </Button>
      </div>
      <Button type="submit" form="secret-edit-form"> save changes </Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, toRef } from 'vue'
import { Dialog, Button, InputText, Password, AutoComplete } from 'primevue'
import { Form } from '@primevue/forms'
import { Bolt } from 'lucide-vue-next'
import { useToast } from 'primevue/usetoast'
import type { OrbitSecret } from '@/lib/api/orbit-secrets/interfaces'
import { useOrbitSecretForm } from '@/hooks/useOrbitSecretForm'
import { simpleErrorToast } from '@/lib/primevue/data/toasts'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import type { FormSubmitEvent } from '@primevue/forms'

interface Props {
  visible: boolean
  secret?: OrbitSecret | null
}

const props = defineProps<Props>()
const emit = defineEmits(['update:visible'])
const toast = useToast()

const dialogPt = {
  footer: { style: 'display: flex; justify-content: space-between; width: 100%; margin-top: auto;' },
}

const {
  formState,
  secretSchema,
  autocompleteItems,
  searchTags,
  submitForm,
  handleDelete,
} = useOrbitSecretForm(toRef(props, 'secret'), {
  onSuccess: () => emit('update:visible', false),
});

const secretResolver = computed(() => zodResolver(secretSchema.value));

async function onComponentSubmit({ valid }: FormSubmitEvent) {
  try {
    await submitForm();
  } catch (e) {
    console.error("Schema validation failed", e)
    return
  }
}

async function onComponentDelete() {
  try {
    handleDelete()
  } catch (e: any) {
    toast.add(simpleErrorToast(e?.response?.data?.detail || e.message || 'Failed to delete secret'))
  }
}
</script>

<style scoped>

.dialog-title {
  font-weight: 500;
  font-size: 16px;
  text-transform: uppercase;
  display: flex;
  gap: 8px;
  align-items: center;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
  font-weight: 500;
  align-self: flex-start;
}
</style>

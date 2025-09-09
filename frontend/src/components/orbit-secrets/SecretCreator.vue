<template>
  <Dialog
    v-model:visible="visible"
    header="Create a new secret"
    modal
    :draggable="false"
    :pt="dialogPt"
  >
    <Form 
    id="secret-create-form" 
    class="form" 
    :resolver="secretResolver" 
    @submit="onComponentSubmit"
    >
      <div class="form-item">
        <label for="name" class="label required">Name</label>
        <InputText 
        v-model="formState.name" 
        id="name" 
        name="name" 
        autofocus 
        />
      </div>

      <div class="form-item">
        <label for="value" class="label required">Secret key</label>
        <Password 
        v-model="formState.value" 
        id="value" 
        name="value" 
        :feedback="false" 
        toggleMask fluid
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
      <Button type="submit" form="secret-create-form" fluid  rounded> Create </Button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Dialog, Button, InputText, Password, AutoComplete } from 'primevue'
import { Form } from '@primevue/forms'
import type { DialogPassThroughOptions } from 'primevue'
import { useToast } from 'primevue/usetoast'
import { useOrbitSecretForm } from '@/hooks/useOrbitSecretForm'
import { simpleErrorToast } from '@/lib/primevue/data/toasts'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import type { FormSubmitEvent } from '@primevue/forms'


const visible = defineModel<boolean>('visible')
const toast = useToast()

const dialogPt: DialogPassThroughOptions = {
  root: { style: 'max-width: 500px; width: 100%;' },
  header: { style: 'padding: 28px; text-transform: uppercase; font-size: 20px;' },
  content: { style: 'padding: 0 28px 28px;' },
}

const {
  formState,
  secretSchema,
  autocompleteItems,
  searchTags,
  submitForm,
  resetForm,
} = useOrbitSecretForm(ref(null), {
  onSuccess: () => { visible.value = false },
});

const secretResolver = computed(() => zodResolver(secretSchema.value));

async function onComponentSubmit({ valid }: FormSubmitEvent) {
  if (!valid) return;
  try {
    await submitForm();
  } catch (e: any) {
    toast.add(simpleErrorToast(e?.response?.data?.detail || e.message || 'Failed to create secret'));
  }
}

watch(visible, (v) => {
  if (v) {
    resetForm();
  }
});
</script>

<style scoped>

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
  font-weight: 400;
  align-self: flex-start;
}

.p-error {
  color: var(--p-red-500);
  font-size: 12px;
}
</style>

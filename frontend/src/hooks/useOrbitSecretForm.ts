import { ref, computed, watch } from 'vue';
import type { Ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import * as z from 'zod';

import { useSecretsStore } from '@/stores/orbit-secrets';
import { useOrbitsStore } from '@/stores/orbits';
import { simpleSuccessToast } from '@/lib/primevue/data/toasts';
import { deleteSecretConfirmation } from '@/lib/primevue/data/confirm';
import type { AutoCompleteCompleteEvent } from 'primevue/autocomplete';
import type { OrbitSecret, UpdateSecretPayload, CreateSecretPayload } from '@/lib/api/orbit-secrets/interfaces';

interface UseSecretFormOptions {
	onSuccess: () => void;
}

export function useOrbitSecretForm(secret: Ref < OrbitSecret | null | undefined > , options: UseSecretFormOptions) {
	const secretsStore = useSecretsStore();
	const orbitsStore = useOrbitsStore();
	const toast = useToast();
	const confirm = useConfirm();

	const isEditMode = computed(() => !!secret.value?.id);

	const secretSchema = computed(() =>
		z.object({
			name: z.string()
				.trim()
				.refine(
					(name) => {
						const normalized = name.trim().toLowerCase()
						const currentName = secret.value?.name?.trim().toLowerCase()

						if (isEditMode.value && normalized === currentName) {
							return true
						}
						if (normalized.length < 1) {
							return false
						}
						const existingSecret = secretsStore.secretsList.find(
							(s) =>
							s.name.trim().toLowerCase() === normalized &&
							s.id !== secret.value?.id
						)
						if (existingSecret) {
							return false
						}
						return true
					}, {
						message: 'A secret with this name already exists or is too short'
					}
				),
			value: isEditMode.value ?
				z.string().optional() :
				z.string().trim().min(1),
			tags: z.array(z.string()).optional().default([]),
		})
	)

	const formState = ref({
		name: '',
		value: '',
		tags: [] as string[],
	});

	const autocompleteItems = ref < string[] > ([]);
	const existingTags = computed(() => secretsStore.existingTags);

	function searchTags(event: AutoCompleteCompleteEvent) {
		const query = event.query.toLowerCase();
		autocompleteItems.value = [
			event.query,
			...existingTags.value.filter((tag: string) => tag.toLowerCase().includes(query)),
		];
	}

	function resetForm() {
		formState.value = {
			name: '',
			value: '',
			tags: [],
		};
	}

	const originalSecretState = ref({
		name: '',
		value: '',
		tags: [] as string[],
	});

	const loadSecretDetails = async () => {
		if (!isEditMode.value || !secret.value) return;

		resetForm();

		const currentOrbit = orbitsStore.currentOrbitDetails;
		if (currentOrbit?.organization_id && currentOrbit?.id) {
			const fullSecret = await secretsStore.getSecretById(
				currentOrbit.organization_id, currentOrbit.id, secret.value.id
			);

			if (fullSecret) {
				formState.value.name = fullSecret.name || '';
				formState.value.value = fullSecret.value || '';
				formState.value.tags = [...(fullSecret.tags || [])];

				originalSecretState.value.name = fullSecret.name || '';
				originalSecretState.value.value = fullSecret.value || '';
				originalSecretState.value.tags = [...(fullSecret.tags || [])];

			}
		}
	};

	watch(secret, (newSecret) => {
		if (newSecret?.id) {
			loadSecretDetails();
		} else {
			resetForm();
		}
	}, {
		immediate: true
	});

	async function submitForm() {
		const currentOrbit = orbitsStore.currentOrbitDetails;
		if (!currentOrbit?.organization_id || !currentOrbit?.id) {
			throw new Error("Current orbit details are not available.");
		}

		if (isEditMode.value && secret.value) {
			const updatePayload: UpdateSecretPayload = {
				id: secret.value.id,
				name: formState.value.name.trim(),
				tags: formState.value.tags,
			};

			if (formState.value.value) {
				updatePayload.value = formState.value.value;
			}

			await secretsStore.updateSecret(currentOrbit.organization_id, currentOrbit.id, updatePayload);
			toast.add(simpleSuccessToast('Secret updated successfully'));
		} else {
			const createPayload: CreateSecretPayload = {
				name: formState.value.name.trim(),
				value: formState.value.value.trim(),
				tags: formState.value.tags,
			};

			await secretsStore.addSecret(currentOrbit.organization_id, currentOrbit.id, createPayload);
			toast.add(simpleSuccessToast('Secret created successfully'));
		}

		options.onSuccess();
	}

	const handleDelete = () => {
		if (!isEditMode.value || !secret.value) return;

		confirm.require({
			...deleteSecretConfirmation,
			accept: async () => {
				const currentOrbit = orbitsStore.currentOrbitDetails;
				if (currentOrbit?.organization_id && currentOrbit?.id && secret.value?.id) {
					await secretsStore.deleteSecret(currentOrbit.organization_id, currentOrbit.id, secret.value.id);
					toast.add(simpleSuccessToast('Secret deleted successfully'));
					options.onSuccess();
				}
			}
		});
	};


	return {
		formState,
		isEditMode,
		autocompleteItems,
		secretSchema,
		searchTags,
		submitForm,
		handleDelete,
		resetForm,
	};
}
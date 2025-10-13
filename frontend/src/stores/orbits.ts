import type { OrbitRoleEnum } from '@/components/orbits/orbits.interfaces'
import { dataforceApi } from '@/lib/api'
import type {
  AddMemberToOrbitPayload,
  CreateOrbitPayload,
  Orbit,
  OrbitDetails,
  UpdateOrbitPayload,
} from '@/lib/api/DataforceApi.interfaces'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useOrbitsStore = defineStore('orbit', () => {
  const orbitsList = ref<Orbit[]>([])
  const currentOrbitDetails = ref<OrbitDetails | null>(null)

  const getCurrentOrbitPermissions = computed(() => currentOrbitDetails.value?.permissions)

  async function loadOrbitsList(organizationId: string) {
    orbitsList.value = await dataforceApi.getOrganizationOrbits(organizationId)
  }

  async function createOrbit(organizationId: string, payload: CreateOrbitPayload) {
    const orbit = await dataforceApi.createOrbit(organizationId, payload)
    orbitsList.value.push(orbit)
  }

  async function updateOrbit(organizationId: string, payload: UpdateOrbitPayload) {
    const orbit = await dataforceApi.updateOrbit(organizationId, payload)
    orbitsList.value = orbitsList.value.map((savedOrbit) => {
      if (savedOrbit.id !== orbit.id) return savedOrbit
      return orbit
    })
  }

  async function deleteOrbit(organizationId: string, orbitId: string) {
    await dataforceApi.deleteOrbit(organizationId, orbitId)
    orbitsList.value = orbitsList.value.filter((orbit) => orbit.id !== orbitId)
  }

  async function addMemberToOrbit(organizationId: string, payload: AddMemberToOrbitPayload) {
    return dataforceApi.addMemberToOrbit(organizationId, payload)
  }

  async function getOrbitDetails(organizationId: string, orbitId: string) {
    return dataforceApi.getOrbitDetails(organizationId, orbitId)
  }

  async function deleteMember(organizationId: string, orbitId: string, memberId: string) {
    return dataforceApi.deleteOrbitMember(organizationId, orbitId, memberId)
  }

  async function updateMember(
    organizationId: string,
    orbitId: string,
    data: { id: string; role: OrbitRoleEnum },
  ) {
    return dataforceApi.updateOrbitMember(organizationId, orbitId, data)
  }

  function setCurrentOrbitDetails(details: OrbitDetails | null) {
    currentOrbitDetails.value = details
  }

  function reset() {
    orbitsList.value = []
    currentOrbitDetails.value = null
  }

  return {
    orbitsList,
    currentOrbitDetails,
    getCurrentOrbitPermissions,
    createOrbit,
    addMemberToOrbit,
    getOrbitDetails,
    deleteMember,
    updateMember,
    loadOrbitsList,
    updateOrbit,
    deleteOrbit,
    setCurrentOrbitDetails,
    reset,
  }
})

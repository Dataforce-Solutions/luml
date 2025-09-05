import type { AxiosInstance } from 'axios'
import type {
  CreateSatellitePayload,
  CreateSatelliteResponse,
  RegenerateApiKeyResponse,
  Satellite,
} from './interfaces'

export class SatellitesApi {
  private api: AxiosInstance

  constructor(api: AxiosInstance) {
    this.api = api
  }

  async create(organizationId: number, orbitId: number, payload: CreateSatellitePayload) {
    const { data: responseData } = await this.api.post<CreateSatelliteResponse>(
      `/organizations/${organizationId}/orbits/${orbitId}/satellites`,
      payload,
    )
    return responseData
  }

  async update(
    organizationId: number,
    orbitId: number,
    satelliteId: number,
    payload: CreateSatellitePayload,
  ) {
    const { data: responseData } = await this.api.patch<Satellite>(
      `/organizations/${organizationId}/orbits/${orbitId}/satellites/${satelliteId}`,
      payload,
    )
    return responseData
  }

  async getList(organizationId: number, orbitId: number) {
    const { data: responseData } = await this.api.get<Satellite[]>(
      `/organizations/${organizationId}/orbits/${orbitId}/satellites`,
    )
    return responseData
  }

  async getItem(organizationId: number, orbitId: number, satelliteId: number) {
    const { data: responseData } = await this.api.get<Satellite>(
      `/organizations/${organizationId}/orbits/${orbitId}/satellites/${satelliteId}`,
    )
    return responseData
  }

  async delete(organizationId: number, orbitId: number, satelliteId: number) {
    const { data: responseData } = await this.api.delete(
      `/organizations/${organizationId}/orbits/${orbitId}/satellites/${satelliteId}`,
    )
    return responseData
  }

  async regenerateApiKye(organizationId: number, orbitId: number, satelliteId: number) {
    const { data: responseData } = await this.api.post<RegenerateApiKeyResponse>(
      `/organizations/${organizationId}/orbits/${orbitId}/satellites/${satelliteId}/api-key`,
    )
    return responseData
  }
}

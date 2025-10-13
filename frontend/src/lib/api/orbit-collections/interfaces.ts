export enum OrbitCollectionTypeEnum {
  model = 'model',
  dataset = 'dataset',
}

export interface OrbitCollection {
  id: string
  orbit_id: string
  description: string
  name: string
  collection_type: OrbitCollectionTypeEnum
  tags: string[]
  total_models: number
  created_at: Date
  updated_at: Date
}

export interface OrbitCollectionCreator {
  description: string
  name: string
  collection_type?: OrbitCollectionTypeEnum
  tags: string[]
}

export interface FieldInfo<T = string> {
  key: string
  value: T | null 
  label: string
}

export interface CreateDeploymentForm {
  name: string
  description: string
  tags: string[]
  collectionId: string
  modelId: string
  satelliteId: string
  secretDynamicAttributes: FieldInfo<number>[]
  dynamicAttributes: FieldInfo<string>[]
  secretEnvs: FieldInfo<number>[]
  notSecretEnvs: FieldInfo<string>[]
  customVariables: Omit<FieldInfo<string>, 'label'>[]
  satelliteFields: FieldInfo<string | number>[]
}

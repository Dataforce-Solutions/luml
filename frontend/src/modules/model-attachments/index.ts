import type { ModelAttachmentsProvider, FileNode, FileIndex } from './interfaces/interfaces'

import ModelAttachments from './ModelAttachments.vue'

import {
  ModelAttachmentsDatabaseProvider,
  type ModelAttachmentsProviderConfig,
} from './models/ModelAttachmentsDatabaseProvider'

export type { ModelAttachmentsProvider, ModelAttachmentsProviderConfig, FileNode, FileIndex }

export { ModelAttachments, ModelAttachmentsDatabaseProvider }

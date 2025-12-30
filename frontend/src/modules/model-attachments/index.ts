import type { ModelDownloader, MlModel, FileNode, FileIndex } from './interfaces/interfaces'

import AttachmentsView from './ModelAttachments.vue'

import { useModelAttachments, hasAttachments } from './hooks/useModelAttachments'

export type { ModelDownloader, MlModel, FileNode, FileIndex }

export { AttachmentsView, useModelAttachments, hasAttachments }

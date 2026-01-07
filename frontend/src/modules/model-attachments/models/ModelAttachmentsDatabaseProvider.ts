import type { ModelDownloader } from '@/lib/bucket-service'
import type { MlModel, FileIndex } from '@/lib/api/orbit-ml-models/interfaces'
import type { ModelAttachmentsProvider, FileNode } from '../interfaces/interfaces'

export interface ModelAttachmentsProviderConfig {
  downloader: ModelDownloader
  model: MlModel
  findAttachmentsTarPath: (fileIndex: FileIndex) => string | undefined
  findAttachmentsIndexPath: (fileIndex: FileIndex) => string | undefined
}

export class ModelAttachmentsDatabaseProvider implements ModelAttachmentsProvider {
  private downloader: ModelDownloader
  private model: MlModel
  private findAttachmentsTarPath: (fileIndex: FileIndex) => string | undefined
  private findAttachmentsIndexPath: (fileIndex: FileIndex) => string | undefined

  private tree: FileNode[] = []
  private tarBaseOffset: number = 0
  private attachmentsIndex: FileIndex = {}

  constructor(config: ModelAttachmentsProviderConfig) {
    this.downloader = config.downloader
    this.model = config.model
    this.findAttachmentsTarPath = config.findAttachmentsTarPath
    this.findAttachmentsIndexPath = config.findAttachmentsIndexPath
  }

  async init(): Promise<void> {
    const indexPath = this.findAttachmentsIndexPath(this.model.file_index)
    if (!indexPath) {
      return
    }

    const indexData = await this.downloader.getFileFromBucket<FileIndex>(
      this.model.file_index,
      indexPath,
    )

    const tarPath = this.findAttachmentsTarPath(this.model.file_index)
    if (!tarPath) {
      return
    }

    const tarRange = this.model.file_index[tarPath]
    if (!tarRange) {
      return
    }

    const [tarOffset] = tarRange
    this.tarBaseOffset = tarOffset
    this.attachmentsIndex = indexData
    this.tree = this.buildTreeFromIndex(indexData)
  }

  private buildTreeFromIndex(index: FileIndex): FileNode[] {
    const root: Record<string, any> = {}

    const filePaths = Object.entries(index)
      .filter(([path, [, size]]) => size > 0 && !path.endsWith('/'))
      .map(([path]) => path)

    filePaths.forEach((fullPath) => {
      const path = fullPath.replace(/^attachments\//, '')
      const parts = path.split('/')
      const [, size] = index[fullPath]

      let current = root

      parts.forEach((part, idx) => {
        if (idx === parts.length - 1) {
          current[part] = {
            type: 'file',
            path: fullPath,
            size,
          }
        } else {
          if (!current[part]) {
            current[part] = {
              type: 'folder',
              children: {},
            }
          }
          current = current[part].children
        }
      })
    })

    return this.convertToArray(root)
  }

  private convertToArray(obj: Record<string, any>): FileNode[] {
    return Object.entries(obj).map(([name, data]: [string, any]) => {
      if (data.type === 'file') {
        return {
          name,
          path: data.path,
          type: 'file' as const,
          size: data.size,
        }
      } else {
        return {
          name,
          type: 'folder' as const,
          children: this.convertToArray(data.children),
        }
      }
    })
  }

  getDownloader(): ModelDownloader {
    return this.downloader
  }

  getDownloadUrl(): string {
    return this.downloader.url
  }

  getAttachmentsIndex(): FileIndex {
    return this.attachmentsIndex
  }

  getTarBaseOffset(): number {
    return this.tarBaseOffset
  }

  getTree(): FileNode[] {
    return this.tree
  }

  isEmpty(): boolean {
    return this.tree.length === 0
  }
}

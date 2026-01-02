import { ref } from 'vue'
import type { ModelDownloader, MlModel, FileIndex, FileNode } from '../interfaces/interfaces'

const ATTACHMENTS_TAR_REGEX =
  /meta_artifacts\/dataforce\.studio~c~~c~experiment_snapshot~c~v1~~et~~[^/]+\/attachments\.tar$/
const ATTACHMENTS_INDEX_REGEX =
  /meta_artifacts\/dataforce\.studio~c~~c~experiment_snapshot~c~v1~~et~~[^/]+\/attachments\.index\.json$/

export function hasAttachments(fileIndex: FileIndex): boolean {
  return !!Object.keys(fileIndex).find((path) => ATTACHMENTS_TAR_REGEX.test(path))
}

export function useModelAttachments() {
  const tree = ref<FileNode[]>([])
  const tarBaseOffset = ref(0)
  const attachmentsIndex = ref<FileIndex>({})
  const downloadUrl = ref('')
  const selectedFile = ref<FileNode | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function init(downloader: ModelDownloader, model: MlModel): Promise<void> {
    loading.value = true
    error.value = null

    try {
      downloadUrl.value = downloader.url

      const indexPath = findAttachmentsIndexPath(model.file_index)
      if (!indexPath) {
        return
      }

      const indexData = await downloader.getFileFromBucket<FileIndex>(model.file_index, indexPath)

      const tarPath = findAttachmentsTarPath(model.file_index)
      if (!tarPath) {
        return
      }

      const tarRange = model.file_index[tarPath]
      if (!tarRange) {
        return
      }

      const [tarOffset] = tarRange
      tarBaseOffset.value = tarOffset
      attachmentsIndex.value = indexData
      tree.value = buildTreeFromIndex(indexData)
    } catch (e) {
      console.error('Failed to initialize attachments:', e)
      error.value = e instanceof Error ? e.message : 'Unknown error'
      throw e
    } finally {
      loading.value = false
    }
  }

  function findAttachmentsTarPath(fileIndex: FileIndex): string | undefined {
    return Object.keys(fileIndex).find((path) => ATTACHMENTS_TAR_REGEX.test(path))
  }

  function findAttachmentsIndexPath(fileIndex: FileIndex): string | undefined {
    return Object.keys(fileIndex).find((path) => ATTACHMENTS_INDEX_REGEX.test(path))
  }

  function buildTreeFromIndex(index: FileIndex): FileNode[] {
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

    return convertToArray(root)
  }

  function convertToArray(obj: Record<string, any>): FileNode[] {
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
          children: convertToArray(data.children),
        }
      }
    })
  }

  function selectFile(file: FileNode | null) {
    if (file?.type === 'file') {
      selectedFile.value = file
    }
  }

  function isEmpty(): boolean {
    return tree.value.length === 0
  }

  function reset() {
    tree.value = []
    tarBaseOffset.value = 0
    attachmentsIndex.value = {}
    downloadUrl.value = ''
    selectedFile.value = null
    error.value = null
  }

  return {
    tree,
    tarBaseOffset,
    attachmentsIndex,
    downloadUrl,
    selectedFile,
    loading,
    error,
    init,
    selectFile,
    isEmpty,
    reset,
  }
}

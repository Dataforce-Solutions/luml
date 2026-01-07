import { getFileType } from './fileTypes'
import { processFileContent } from './fileContentProcessors'
import type { FetchFileContentParams, FileContentResult } from '../interfaces/interfaces'

const MAX_PREVIEW_SIZE = 10 * 1024 * 1024

export async function fetchFileContent(params: FetchFileContentParams): Promise<FileContentResult> {
  const { file, fileIndex, tarBaseOffset, downloader } = params

  if (!file.path || file.type !== 'file') {
    return {}
  }

  const fileType = getFileType(file.name)
  if (!fileType) {
    return { error: 'unsupported' }
  }

  try {
    const rangeData = fileIndex[file.path]
    if (!rangeData) {
      return { error: 'not-found' }
    }

    const [, length] = rangeData

    if (length === 0) {
      return { error: 'empty' }
    }

    if (length > MAX_PREVIEW_SIZE) {
      return { error: 'too-big' }
    }

    const arrayBuffer = await downloader.getFileFromBucket<ArrayBuffer>(
      fileIndex,
      file.path,
      true,
      tarBaseOffset,
    )
    const fileBlob = new Blob([arrayBuffer])

    const processed = await processFileContent(fileBlob, fileType, file.name)

    return {
      blob: fileBlob,
      text: processed.text,
      contentUrl: processed.contentUrl,
    }
  } catch (e) {
    console.error('Failed to fetch file content:', e)
    return { error: 'unknown' }
  }
}

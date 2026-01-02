import { getFileType } from './fileTypes'
import { processFileContent } from './fileContentProcessors'
import type { FetchFileContentParams, FileContentResult } from '../interfaces/interfaces'

const MAX_PREVIEW_SIZE = 10 * 1024 * 1024

export async function fetchFileContent(params: FetchFileContentParams): Promise<FileContentResult> {
  const { file, fileIndex, tarBaseOffset, downloadUrl } = params

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

    const [offsetInTar, length] = rangeData

    if (length === 0) {
      return { error: 'empty' }
    }

    if (length > MAX_PREVIEW_SIZE) {
      return { error: 'too-big' }
    }

    if (typeof tarBaseOffset !== 'number' || !downloadUrl) {
      throw new Error('TAR metadata not found')
    }

    const absoluteOffset = tarBaseOffset + offsetInTar
    const fileBlob = await fetchFileBlob(downloadUrl, absoluteOffset, length)
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

async function fetchFileBlob(url: string, offset: number, length: number): Promise<Blob> {
  const end = offset + length - 1
  const response = await fetch(url, {
    headers: { Range: `bytes=${offset}-${end}` },
  })

  if (!response.ok) {
    throw new Error(`HTTP Error: ${response.status}`)
  }

  return response.blob()
}

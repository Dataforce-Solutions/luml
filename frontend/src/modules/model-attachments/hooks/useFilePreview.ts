import { ref, watch } from 'vue'
import { fetchFileContent } from '../utils/fileContentFetcher'
import type {
  PreviewState,
  FileContentError,
  UseFilePreviewOptions,
} from '../interfaces/interfaces'

export function useFilePreview(options: UseFilePreviewOptions) {
  const { file, fileIndex, tarBaseOffset, downloader } = options

  const error = ref<string | null>(null)
  const contentUrl = ref<string | null>(null)
  const textContent = ref<string | null>(null)
  const contentBlob = ref<Blob | null>(null)
  const previewState = ref<PreviewState>(null)

  const cleanup = () => {
    if (contentUrl.value) {
      URL.revokeObjectURL(contentUrl.value)
      contentUrl.value = null
    }
    textContent.value = null
    contentBlob.value = null
    error.value = null
  }

  const loadContent = async () => {
    cleanup()

    if (!file.value || !downloader.value) {
      previewState.value = null
      return
    }

    previewState.value = 'loading'

    try {
      const result = await fetchFileContent({
        file: file.value,
        fileIndex: fileIndex.value,
        tarBaseOffset: tarBaseOffset.value,
        downloader: downloader.value,
      })

      if (result.error) {
        error.value = getErrorMessage(result.error)
        previewState.value = mapErrorToState(result.error)
        return
      }

      contentUrl.value = result.contentUrl ?? null
      textContent.value = result.text ?? null
      contentBlob.value = result.blob ?? null
      previewState.value = null
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      previewState.value = 'error'
    }
  }

  const mapErrorToState = (errorType: FileContentError): PreviewState => {
    switch (errorType) {
      case 'unsupported':
        return 'unsupported'
      case 'empty':
        return 'empty'
      case 'too-big':
        return 'too-big'
      default:
        return 'error'
    }
  }

  const getErrorMessage = (errorType: FileContentError): string => {
    switch (errorType) {
      case 'unsupported':
        return 'This file type is not supported for preview'
      case 'not-found':
        return 'File not found in archive'
      case 'empty':
        return 'File is empty'
      case 'too-big':
        return 'File is too large for preview (max 10 MB)'
      default:
        return 'Failed to load file'
    }
  }

  const downloadFile = (fileName: string) => {
    if (!contentBlob.value) return

    const url = URL.createObjectURL(contentBlob.value)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  watch(file, loadContent, { immediate: true })

  return {
    error,
    contentUrl,
    textContent,
    contentBlob,
    previewState,
    downloadFile,
  }
}

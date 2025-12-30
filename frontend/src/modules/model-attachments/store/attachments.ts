import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FileNode } from '../interfaces/interfaces'

export const useModelAttachmentsStore = defineStore('model-attachments', () => {
  const selectedFile = ref<FileNode | null>(null)

  function selectFile(file: FileNode | null) {
    if (file?.type === 'file') {
      selectedFile.value = file
    }
  }

  function reset() {
    selectedFile.value = null
  }

  return {
    selectedFile,
    selectFile,
    reset,
  }
})

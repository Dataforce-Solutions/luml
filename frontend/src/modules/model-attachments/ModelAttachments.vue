<template>
  <div class="attachments-wrapper">
    <template v-if="isEmpty()">
      <div class="empty-state">
        <p>This attachment is empty.</p>
      </div>
    </template>
    <template v-else>
      <FileTree :tree="tree" :selected="selectedFile" @select="selectFile" />
      <FilePreview
        :file-name="fileName"
        :file-size="fileSize"
        :file-path="filePath"
        :file-type="fileType"
        :preview-state="previewState"
        :error-message="previewError || undefined"
        :content-url="contentUrl"
        :text-content="textContent"
        :content-blob="contentBlob"
        @copy-path="handleCopyPath"
        @download="handleDownload"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, toRef } from 'vue'
import { useToast } from 'primevue'
import FileTree from './components/FileTree.vue'
import FilePreview from './components/FilePreview.vue'
import { useFilePreview } from './hooks/useFilePreview'
import { getFileType } from './utils/fileTypes'

interface Props {
  tree: import('./interfaces/interfaces').FileNode[]
  selectedFile: import('./interfaces/interfaces').FileNode | null
  attachmentsIndex: import('./interfaces/interfaces').FileIndex
  tarBaseOffset: number
  downloadUrl: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', node: import('./interfaces/interfaces').FileNode): void
}>()

const toast = useToast()

const {
  error: previewError,
  contentUrl,
  textContent,
  contentBlob,
  downloadFile,
  previewState,
} = useFilePreview({
  file: toRef(() => props.selectedFile),
  fileIndex: toRef(() => props.attachmentsIndex),
  tarBaseOffset: toRef(() => props.tarBaseOffset),
  downloadUrl: toRef(() => props.downloadUrl),
})

const fileName = computed(() => props.selectedFile?.name || '')
const fileSize = computed(() => props.selectedFile?.size || 0)
const filePath = computed(() => props.selectedFile?.path || '')
const fileType = computed(() => (props.selectedFile ? getFileType(props.selectedFile.name) : null))

function isEmpty(): boolean {
  return props.tree.length === 0
}

function selectFile(node: import('./interfaces/interfaces').FileNode) {
  emit('select', node)
}

async function handleCopyPath() {
  if (!props.selectedFile?.path) return
  await navigator.clipboard.writeText(props.selectedFile.path)
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Path copied to clipboard',
    life: 3000,
  })
}

function handleDownload() {
  if (!props.selectedFile) return
  downloadFile(props.selectedFile.name)
}
</script>

<style scoped>
.attachments-wrapper {
  display: flex;
  gap: 16px;
  height: calc(100vh - 320px);
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--p-form-field-float-label-color);
}
</style>

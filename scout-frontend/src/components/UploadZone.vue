<template>
  <div class="space-y-6">
    <!-- Resume upload (required) — D-02 -->
    <div
      class="border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer"
      :class="isDragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/30 hover:border-primary/50'"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop($event, 'resume')"
      @click="resumeInput?.click()"
      role="button"
      aria-label="Upload resume file"
    >
      <div class="flex flex-col items-center gap-2">
        <svg class="w-10 h-10 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <div>
          <p class="text-sm font-medium">
            {{ resumeFile ? resumeFile.name : 'Drag &amp; drop your resume here' }}
          </p>
          <p class="text-xs text-muted-foreground mt-1">PDF or Word (.docx) · Required</p>
        </div>
        <Badge v-if="resumeFile" variant="secondary" class="mt-1">
          {{ (resumeFile.size / 1024).toFixed(0) }} KB
        </Badge>
      </div>
      <input
        ref="resumeInput"
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        class="hidden"
        @change="handleFileInput($event, 'resume')"
      />
    </div>

    <!-- Validation error -->
    <p v-if="resumeError" class="text-sm text-destructive flex items-center gap-1">
      <span>{{ resumeError }}</span>
    </p>

    <!-- Paper PDF upload (optional) — D-02, D-04 -->
    <div class="space-y-2">
      <Label class="text-sm font-medium">
        Academic Paper PDF <span class="text-muted-foreground font-normal">(optional)</span>
      </Label>
      <div
        class="border border-dashed rounded-lg p-4 text-center cursor-pointer hover:border-primary/50 transition-colors"
        @click="paperInput?.click()"
      >
        <p class="text-sm text-muted-foreground">
          {{ paperFile ? paperFile.name : 'Click to upload paper PDF' }}
        </p>
      </div>
      <input
        ref="paperInput"
        type="file"
        accept=".pdf,application/pdf"
        class="hidden"
        @change="handleFileInput($event, 'paper')"
      />
    </div>

    <!-- GitHub URL (optional) — D-02 -->
    <div class="space-y-2">
      <Label for="github-url" class="text-sm font-medium">
        GitHub Profile URL <span class="text-muted-foreground font-normal">(optional)</span>
      </Label>
      <Input
        id="github-url"
        v-model="githubUrl"
        type="url"
        placeholder="https://github.com/yourusername"
        class="w-full"
      />
    </div>

    <!-- Submit button -->
    <Button
      @click="handleSubmit"
      :disabled="!resumeFile || isUploading"
      class="w-full"
      size="lg"
    >
      <span v-if="isUploading">Uploading...</span>
      <span v-else>Parse Resume</span>
    </Button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { uploadWithProgress, type UploadProgressEvent } from '@/services/api'

const emit = defineEmits<{
  progress: [event: UploadProgressEvent]
  complete: [resumeId: number]
  error: [message: string]
}>()

const resumeInput = ref<HTMLInputElement | null>(null)
const paperInput = ref<HTMLInputElement | null>(null)
const resumeFile = ref<File | null>(null)
const paperFile = ref<File | null>(null)
const githubUrl = ref('')
const isDragOver = ref(false)
const isUploading = ref(false)
const resumeError = ref('')

const ALLOWED_RESUME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]
const ALLOWED_RESUME_EXTS = ['.pdf', '.docx']

function validateResumeFile(file: File): string {
  if (
    !ALLOWED_RESUME_TYPES.includes(file.type) &&
    !ALLOWED_RESUME_EXTS.some(ext => file.name.toLowerCase().endsWith(ext))
  ) {
    return 'Please upload a PDF or Word (.docx) file'
  }
  if (file.size > 20 * 1024 * 1024) {
    return 'File must be under 20 MB'
  }
  return ''
}

function handleDrop(event: DragEvent, target: 'resume' | 'paper') {
  isDragOver.value = false
  const file = event.dataTransfer?.files[0]
  if (!file) return
  setFile(file, target)
}

function handleFileInput(event: Event, target: 'resume' | 'paper') {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  setFile(file, target)
}

function setFile(file: File, target: 'resume' | 'paper') {
  if (target === 'resume') {
    const err = validateResumeFile(file)
    resumeError.value = err
    if (!err) resumeFile.value = file
  } else {
    paperFile.value = file
  }
}

async function handleSubmit() {
  if (!resumeFile.value) {
    resumeError.value = 'Resume is required'
    return
  }

  isUploading.value = true
  resumeError.value = ''

  const formData = new FormData()
  formData.append('resume', resumeFile.value)
  if (paperFile.value) formData.append('paper', paperFile.value)
  if (githubUrl.value.trim()) formData.append('github_url', githubUrl.value.trim())

  try {
    const resumeId = await uploadWithProgress(formData, event => {
      emit('progress', event)
    })
    emit('complete', resumeId)
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Upload failed'
    emit('error', msg)
  } finally {
    isUploading.value = false
  }
}
</script>

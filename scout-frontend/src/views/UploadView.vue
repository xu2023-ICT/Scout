<template>
  <!-- D-05: single-page scrolling layout -->
  <div class="min-h-screen bg-background">
    <div class="max-w-2xl mx-auto px-4 py-12">

      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold tracking-tight">Upload Your Resume</h1>
        <p class="mt-2 text-muted-foreground">
          Scout will parse your resume and materials, then let you review and confirm.
        </p>
      </div>

      <!-- Upload zone — D-01, D-02, D-03 -->
      <Card class="p-6 mb-6">
        <UploadZone
          v-if="!isParsing && !isDone"
          @progress="handleProgress"
          @complete="handleComplete"
          @error="handleError"
        />

        <!-- Progress display — shown during parsing -->
        <ParseProgress
          v-if="isParsing || errorMessage"
          :current-event="latestProgressEvent"
          :error-message="errorMessage"
          :has-paper="hasPaper"
          @retry="handleRetry"
        />

        <!-- Done state — brief confirmation before redirect -->
        <div v-if="isDone" class="text-center py-4 space-y-2">
          <div class="text-4xl">&#10003;</div>
          <p class="font-medium">Parsing complete!</p>
          <p class="text-sm text-muted-foreground">Redirecting to review...</p>
        </div>
      </Card>

      <!-- Info cards -->
      <div v-if="!isParsing && !isDone" class="grid grid-cols-2 gap-4 mt-6 text-sm text-muted-foreground">
        <div class="rounded-lg border p-4">
          <p class="font-medium text-foreground mb-1">What's parsed</p>
          <ul class="space-y-1">
            <li>Work experience</li>
            <li>Education</li>
            <li>Skills</li>
            <li>Projects</li>
          </ul>
        </div>
        <div class="rounded-lg border p-4">
          <p class="font-medium text-foreground mb-1">Your data</p>
          <ul class="space-y-1">
            <li>Stored locally</li>
            <li>You can edit after parsing</li>
            <li>Used only for job matching</li>
          </ul>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Card } from '@/components/ui/card'
import UploadZone from '@/components/UploadZone.vue'
import ParseProgress from '@/components/ParseProgress.vue'
import { useResumeStore } from '@/stores/resume'
import type { UploadProgressEvent } from '@/services/api'

const router = useRouter()
const resumeStore = useResumeStore()

const isParsing = ref(false)
const isDone = ref(false)
const errorMessage = ref('')
const latestProgressEvent = ref<UploadProgressEvent | null>(null)
const hasPaper = ref(false)

function handleProgress(event: UploadProgressEvent) {
  isParsing.value = true
  latestProgressEvent.value = event
}

async function handleComplete(resumeId: number) {
  isDone.value = true
  isParsing.value = false
  await resumeStore.loadParsed(resumeId)
  // Brief pause so user sees "complete" state before redirect
  setTimeout(() => {
    router.push(`/review/${resumeId}`)
  }, 800)
}

function handleError(message: string) {
  isParsing.value = false
  errorMessage.value = message
}

function handleRetry() {
  isParsing.value = false
  isDone.value = false
  errorMessage.value = ''
  latestProgressEvent.value = null
  resumeStore.reset()
}
</script>

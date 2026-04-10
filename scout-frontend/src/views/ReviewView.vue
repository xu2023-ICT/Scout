<template>
  <div class="min-h-screen bg-background">
    <div class="container max-w-3xl mx-auto py-8 px-4">
      <div class="mb-6">
        <h1 class="text-2xl font-bold">Review &amp; Confirm Your Resume</h1>
        <p class="text-muted-foreground mt-1">
          Check the AI-parsed data below. Edit any fields that need correction, then confirm when ready.
        </p>
      </div>

      <!-- Loading state -->
      <div v-if="resumeStore.isLoading" class="flex items-center justify-center py-16">
        <div class="text-center space-y-2">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p class="text-sm text-muted-foreground">Loading resume data...</p>
        </div>
      </div>

      <!-- Error state -->
      <div v-else-if="resumeStore.error" class="rounded-lg border border-destructive/50 bg-destructive/5 p-6 text-center">
        <p class="text-destructive font-medium">Failed to load resume</p>
        <p class="text-sm text-muted-foreground mt-1">{{ resumeStore.error }}</p>
      </div>

      <!-- Form -->
      <ResumeForm v-else-if="resumeStore.parsedData" />

      <!-- Empty state (shouldn't normally happen) -->
      <div v-else class="text-center py-16 text-muted-foreground">
        <p>No resume data found. Please upload a resume first.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useResumeStore } from '@/stores/resume'
import ResumeForm from '@/components/ResumeForm/ResumeForm.vue'

const props = defineProps<{ id: string }>()
const resumeStore = useResumeStore()

onMounted(() => {
  resumeStore.loadParsed(Number(props.id))
})
</script>

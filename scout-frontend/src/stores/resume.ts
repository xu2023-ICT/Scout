import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PaperParsed, ParsedResume } from '@/types/resume'

export const useResumeStore = defineStore('resume', () => {
  const resumeId = ref<number | null>(null)
  const parsedData = ref<ParsedResume | null>(null)
  const paperData = ref<PaperParsed | null>(null)
  const githubUrl = ref<string | null>(null)
  const isConfirmed = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function loadParsed(id: number) {
    isLoading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/resume/${id}`)
      if (!res.ok) throw new Error(`Failed to fetch resume: ${res.status}`)
      const data = await res.json()
      parsedData.value = data.parsed_data
      paperData.value = data.paper ?? null
      githubUrl.value = data.github_url ?? null
      resumeId.value = id
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
    } finally {
      isLoading.value = false
    }
  }

  async function saveEdits(updated: ParsedResume) {
    if (!resumeId.value) return
    const res = await fetch(`/api/resume/${resumeId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ parsed_data: updated, github_url: githubUrl.value }),
    })
    if (!res.ok) throw new Error('Failed to save edits')
  }

  async function confirmResume() {
    if (!resumeId.value) return
    const res = await fetch(`/api/resume/${resumeId.value}/confirm`, { method: 'POST' })
    if (!res.ok) throw new Error('Failed to confirm resume')
    isConfirmed.value = true
  }

  function reset() {
    resumeId.value = null
    parsedData.value = null
    paperData.value = null
    githubUrl.value = null
    isConfirmed.value = false
    error.value = null
  }

  return {
    resumeId,
    parsedData,
    paperData,
    githubUrl,
    isConfirmed,
    isLoading,
    error,
    loadParsed,
    saveEdits,
    confirmResume,
    reset,
  }
})

export const API_BASE = '/api'

export interface UploadProgressEvent {
  step: 'extracting' | 'parsing_resume' | 'parsing_paper' | 'saving' | 'done'
  pct: number
  resume_id?: number
  error?: string
}

export type ProgressCallback = (event: UploadProgressEvent) => void

/**
 * Upload resume and optional materials, streaming progress via SSE.
 * Falls back to simulated progress if SSE endpoint not available.
 */
export async function uploadWithProgress(
  formData: FormData,
  onProgress: ProgressCallback,
): Promise<number> {
  return await uploadWithSimulatedProgress(formData, onProgress)
}

async function uploadWithSimulatedProgress(
  formData: FormData,
  onProgress: ProgressCallback,
): Promise<number> {
  // Emit fake progress while waiting for response
  const steps: UploadProgressEvent[] = [
    { step: 'extracting', pct: 10 },
    { step: 'parsing_resume', pct: 40 },
  ]
  if (formData.get('paper')) {
    steps.push({ step: 'parsing_paper', pct: 70 })
  }
  steps.push({ step: 'saving', pct: 90 })

  let stepIdx = 0
  const interval = setInterval(() => {
    const step = steps[stepIdx]
    if (stepIdx < steps.length && step) {
      onProgress(step)
      stepIdx++
    }
  }, 1200) // 1.2s per fake step

  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    })
    clearInterval(interval)
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Upload failed')
    }
    const data = await response.json()
    onProgress({ step: 'done', pct: 100, resume_id: data.resume_id })
    return data.resume_id as number
  } catch (e) {
    clearInterval(interval)
    throw e
  }
}

export async function getResume(id: number) {
  const res = await fetch(`${API_BASE}/resume/${id}`)
  if (!res.ok) throw new Error('Failed to fetch resume')
  return res.json()
}

export async function updateResume(id: number, data: unknown) {
  const res = await fetch(`${API_BASE}/resume/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to update resume')
  return res.json()
}

export async function confirmResume(id: number) {
  const res = await fetch(`${API_BASE}/resume/${id}/confirm`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to confirm resume')
  return res.json()
}

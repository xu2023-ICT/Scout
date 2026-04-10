export const API_BASE = '/api'

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

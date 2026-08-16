import type { Evaluation, EvaluationInput, ReviewItem } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api/v1'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  } catch {
    throw new Error('The AnswerTrust API is unavailable. Start FastAPI and try again.')
  }
  const body = await response.json()
  if (!response.ok) throw new Error(body.error?.message ?? 'The request could not be completed.')
  return body as T
}

export function createEvaluation(input: EvaluationInput) {
  return request<Evaluation>('/evaluations', { method: 'POST', body: JSON.stringify(input) })
}

export function getEvaluation(id: string) {
  return request<Evaluation>(`/evaluations/${encodeURIComponent(id)}`)
}

export function getPendingReviews() { return request<ReviewItem[]>('/reviews/pending') }
export function submitReview(id: string, decision: 'APPROVE' | 'REJECT', notes: string) {
  return request(`/evaluations/${encodeURIComponent(id)}/review`, { method: 'POST', body: JSON.stringify({ decision, notes }) })
}

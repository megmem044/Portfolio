import { describe, expect, it } from 'vitest'
import { importErrorMessage } from './imports'

describe('import API errors', () => {
  it('uses the FastAPI detail message when one is returned', async () => {
    const response = new Response(JSON.stringify({ detail: 'CSV header is required' }), {
      status: 422,
      headers: { 'Content-Type': 'application/json' },
    })

    await expect(importErrorMessage(response)).resolves.toBe('CSV header is required')
  })

  it('falls back safely when the response is not JSON', async () => {
    const response = new Response('upstream failure', { status: 502 })

    await expect(importErrorMessage(response)).resolves.toBe('The import request failed.')
  })
})

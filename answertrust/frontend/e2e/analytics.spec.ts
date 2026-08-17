import { expect, test } from '@playwright/test'

test('an administrator can view persistent analytics', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('answertrust_token', 'test-token')
    localStorage.setItem('answertrust_user', JSON.stringify({ user_id: 'admin-1', email: 'admin@example.com', role: 'ADMIN' }))
  })
  await page.route('**/api/v1/analytics', route => route.fulfill({ json: {
    total_evaluations: 20,
    average_evaluation_latency_ms: 42.5,
    open_reviews: 3,
    resolved_reviews: 5,
    decision_counts: { PUBLISH: 10, REVIEW: 6, REJECT: 4 },
    review_counts: { APPROVE: 2, REJECT: 3 },
    benchmark_history: [{ run_id: 'run-1', started_at: '2026-08-16T12:00:00Z', decision_accuracy_pct: 98, false_publish_rate_pct: 0 }],
  } }))

  await page.goto('/analytics')
  await expect(page.getByRole('heading', { name: 'How AnswerTrust is performing.' })).toBeVisible()
  await expect(page.getByText('20').first()).toBeVisible()
  await expect(page.getByText('98% accuracy')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Analytics' })).toBeVisible()
})

import { expect, test } from '@playwright/test'
import { reviewEvaluation } from './fixtures'

test('a reviewer can resolve an evaluation', async ({ page }) => {
  const item = { question: 'Did walking help everyone?', answer: 'Walking helped everyone.', evaluation: reviewEvaluation, reviewed: false }
  await page.route('**/api/v1/reviews/pending', route => route.fulfill({ json: [item] }))
  await page.route('**/api/v1/evaluations/review-123/review', async route => {
    expect(route.request().postDataJSON()).toEqual({ decision: 'REJECT', notes: 'The answer overstates the result.' })
    await route.fulfill({ json: { evaluation_id: 'review-123', system_decision: 'REVIEW', reviewer_decision: 'REJECT', reviewer_notes: 'The answer overstates the result.' } })
  })

  await page.goto('/review')
  await expect(page.getByText('1 awaiting review')).toBeVisible()
  await page.getByLabel('Reviewer notes').fill('The answer overstates the result.')
  await page.getByRole('button', { name: 'Reject' }).click()

  await expect(page.getByText('Review queue clear')).toBeVisible()
})

test('shows the empty review state', async ({ page }) => {
  await page.route('**/api/v1/reviews/pending', route => route.fulfill({ json: [] }))
  await page.goto('/review')
  await expect(page.getByText('Review queue clear')).toBeVisible()
})

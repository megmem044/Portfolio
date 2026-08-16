import { expect, test } from '@playwright/test'
import { evaluation } from './fixtures'

test('submits an answer and shows its claim audit', async ({ page }) => {
  await page.route('**/api/v1/evaluations', async route => {
    if (route.request().method() === 'POST') await route.fulfill({ json: evaluation })
    else await route.fallback()
  })
  await page.route('**/api/v1/evaluations/evaluation-123', route => route.fulfill({ json: evaluation }))

  await page.goto('/evaluate')
  await page.getByLabel('Research question').fill('Did walking lower blood pressure?')
  await page.getByLabel('Paper or selected text').fill('RESULTS\nDaily walking lowered blood pressure.')
  await page.getByLabel('AI-generated answer').fill('Daily walking lowered blood pressure.')
  await page.getByRole('button', { name: 'Evaluate claims' }).click()

  await expect(page).toHaveURL(/\/evaluations\/evaluation-123$/)
  await expect(page.getByRole('heading', { name: 'PUBLISH' })).toBeVisible()
  await expect(page.getByText('Daily walking lowered blood pressure.').first()).toBeVisible()
  await expect(page.getByText('96% match')).toBeVisible()
})

test('shows a useful message when the API is unavailable', async ({ page }) => {
  await page.route('**/api/v1/evaluations', route => route.abort())
  await page.goto('/evaluate')
  await page.getByLabel('Research question').fill('Did walking help?')
  await page.getByLabel('Paper or selected text').fill('RESULTS\nWalking helped.')
  await page.getByLabel('AI-generated answer').fill('Walking helped.')
  await page.getByRole('button', { name: 'Evaluate claims' }).click()

  await expect(page.getByRole('alert')).toContainText('API is unavailable')
})

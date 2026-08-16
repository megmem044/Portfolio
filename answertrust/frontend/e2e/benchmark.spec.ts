import { expect, test } from '@playwright/test'
import { benchmark } from './fixtures'

test('runs a publication benchmark and shows its errors', async ({ page }) => {
  await page.route('**/api/v1/benchmarks', async route => {
    if (route.request().method() === 'POST') await route.fulfill({ json: benchmark })
    else await route.fulfill({ json: [] })
  })
  await page.route('**/api/v1/benchmarks/publication', route => route.fulfill({ json: benchmark }))

  await page.goto('/benchmarks')
  await expect(page.getByText('No measured runs yet')).toBeVisible()
  await page.getByRole('button', { name: 'Run publication benchmark' }).click()

  await expect(page.locator('.metric-grid article').filter({ hasText: 'Decision accuracy' }).getByText('98%')).toBeVisible()
  await expect(page.getByText('1 mismatched example')).toBeVisible()
  await expect(page.getByText('part-01')).toBeVisible()
})

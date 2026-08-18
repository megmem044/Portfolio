// Browser checks for sign-in and protected navigation.
import { expect, test } from '@playwright/test'

test('a reviewer can sign in and open the protected workspace', async ({ page }) => {
  await page.route('**/api/v1/auth/login', async route => {
    expect(route.request().postDataJSON()).toEqual({ email: 'reviewer@example.com', password: 'secure-password' })
    await route.fulfill({ json: { access_token: 'signed-token', token_type: 'bearer', user: { user_id: 'user-1', email: 'reviewer@example.com', role: 'REVIEWER' } } })
  })
  await page.route('**/api/v1/reviews/pending', route => route.fulfill({ json: [] }))

  await page.goto('/login')
  await page.getByLabel('Email').fill('reviewer@example.com')
  await page.getByLabel('Password').fill('secure-password')
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page).toHaveURL(/\/review$/)
  await expect(page.getByText('Review queue clear')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible()
})

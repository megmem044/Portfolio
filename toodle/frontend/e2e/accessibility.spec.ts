// Checks the main login and task-dialog workflow with a real browser keyboard.
import { expect, test } from '@playwright/test';

test('keyboard user can sign in and use the task dialog', async ({ page }) => {
  await page.route('**/api/auth/login', (route) => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify({ token: 'test-token', name: 'Test User', email: 'test@example.com' }),
  }));
  await page.route('**/api/bootstrap', (route) => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify({ tasks: [], categories: [] }),
  }));

  await page.goto('/');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  const addTask = page.getByRole('button', { name: 'Add Task' });
  await expect(addTask).toBeVisible();
  await addTask.focus();
  await page.keyboard.press('Enter');

  const dialog = page.getByRole('dialog', { name: 'New Task' });
  await expect(dialog).toBeVisible();
  await expect(page.getByLabel('Title')).toBeFocused();
  await expect(page.getByRole('group', { name: 'Priority' })).toBeVisible();
  await expect(page.getByRole('group', { name: 'Category' })).toBeVisible();

  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(addTask).toBeFocused();
});

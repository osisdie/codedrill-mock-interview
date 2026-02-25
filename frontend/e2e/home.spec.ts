import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('displays hero section and category cards', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByRole('heading', { level: 1 })).toContainText('Sharpen Your Coding Skills')

    const cards = page.locator('button').filter({ hasText: /problems$/ })
    await expect(cards).toHaveCount(4)

    await expect(page.getByRole('heading', { name: 'Algorithms' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'FastAPI' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Django' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Pytest' })).toBeVisible()
  })

  test('shows how-it-works steps', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByText('How It Works')).toBeVisible()
    await expect(page.getByText('Pick a Problem')).toBeVisible()
    await expect(page.getByText('Write Code')).toBeVisible()
    await expect(page.getByText('AI Interview')).toBeVisible()
    await expect(page.getByText('Get Scored')).toBeVisible()
  })

  test('clicking a category card navigates to problems list', async ({ page }) => {
    await page.goto('/')

    await page.getByRole('button').filter({ hasText: 'Algorithms' }).click()

    await expect(page).toHaveURL(/\/problems\/algorithms/)
  })
})

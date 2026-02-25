import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('header links navigate correctly', async ({ page }) => {
    await page.goto('/')

    // Navigate to Problems via header
    await page.getByRole('link', { name: /problems/i }).click()
    await expect(page).toHaveURL(/\/problems/)

    // Navigate to History via header
    await page.getByRole('link', { name: /history/i }).click()
    await expect(page).toHaveURL(/\/history/)

    // Navigate Home via logo/brand
    const homeLink = page.getByRole('link').filter({ hasText: /codedrill|home/i })
    if (await homeLink.count()) {
      await homeLink.first().click()
      await expect(page).toHaveURL('/')
    }
  })

  test('full user flow: home → problems → start session → arena', async ({ page }) => {
    // Start at home
    await page.goto('/')

    // Click Algorithms category
    await page.getByRole('button').filter({ hasText: 'Algorithms' }).click()
    await expect(page).toHaveURL(/\/problems\/algorithms/)

    // Wait for problems to load
    await expect(page.getByText('Loading problems...')).not.toBeVisible({ timeout: 10_000 })

    // Click "Start" on the first problem card
    const startButton = page.getByRole('button', { name: /start/i }).first()
    await expect(startButton).toBeVisible()
    await startButton.click()

    // Should navigate to arena
    await expect(page).toHaveURL(/\/arena\//)

    // Arena should load with problem content
    await expect(page.getByText('solution.py')).toBeVisible({ timeout: 10_000 })
  })
})

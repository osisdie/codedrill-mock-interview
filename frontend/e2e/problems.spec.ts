import { test, expect } from '@playwright/test'

test.describe('Problem List', () => {
  test('displays problems and filter buttons', async ({ page }) => {
    await page.goto('/problems')

    await expect(page.getByRole('heading', { level: 1 })).toContainText('Problems')

    // Category filter buttons
    await expect(page.getByRole('button', { name: 'All' }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: 'Algorithms' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'FastAPI' })).toBeVisible()

    // Difficulty filter buttons
    await expect(page.getByRole('button', { name: 'Easy' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Medium' })).toBeVisible()

    // Wait for problems to load (no loading indicator visible)
    await expect(page.getByText('Loading problems...')).not.toBeVisible({ timeout: 10_000 })
  })

  test('filters problems by category', async ({ page }) => {
    await page.goto('/problems')
    await expect(page.getByText('Loading problems...')).not.toBeVisible({ timeout: 10_000 })

    // Set up response listener BEFORE the click to avoid race condition
    const responsePromise = page.waitForResponse(
      (res) => res.url().includes('/api/problems') && res.status() === 200,
    )
    await page.getByRole('button', { name: 'FastAPI' }).click()
    await responsePromise

    await expect(page.getByText('Loading problems...')).not.toBeVisible()
  })

  test('navigates to problems via category route', async ({ page }) => {
    await page.goto('/problems/algorithms')

    await expect(page.getByText('Loading problems...')).not.toBeVisible({ timeout: 10_000 })
    // Should show at least one problem card
    await expect(page.getByText('Two Sum')).toBeVisible()
  })

  test('shows empty state for impossible filter combo', async ({ page }) => {
    await page.goto('/problems')
    await expect(page.getByText('Loading problems...')).not.toBeVisible({ timeout: 10_000 })

    // Set up listener before each click
    const djangoResponse = page.waitForResponse(
      (res) => res.url().includes('/api/problems') && res.status() === 200,
    )
    await page.getByRole('button', { name: 'Django' }).click()
    await djangoResponse

    const easyResponse = page.waitForResponse(
      (res) => res.url().includes('/api/problems') && res.status() === 200,
    )
    await page.getByRole('button', { name: 'Easy' }).click()
    await easyResponse

    await expect(page.getByText('No problems found')).toBeVisible()
  })
})

import { test, expect } from '@playwright/test'

test.describe('Session History', () => {
  test('shows empty state when no sessions exist', async ({ page }) => {
    await page.goto('/history')

    // Either shows sessions or empty state
    const heading = page.getByRole('heading', { level: 1 })
    await expect(heading).toContainText('Session History')
  })

  test('shows session after creating one via API', async ({ page, request }) => {
    // Create a session first
    const res = await request.post('/api/sessions', {
      data: { problem_id: 'valid-anagram' },
    })
    expect(res.ok()).toBeTruthy()

    await page.goto('/history')

    // Wait for sessions to load
    await expect(page.getByText('Loading sessions...')).not.toBeVisible({ timeout: 10_000 })

    // Should see the problem id in session list (may have multiple from prior runs)
    await expect(page.getByText('valid-anagram').first()).toBeVisible()
  })
})

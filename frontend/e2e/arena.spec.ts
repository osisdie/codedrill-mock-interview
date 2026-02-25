import { test, expect } from '@playwright/test'

test.describe('Coding Arena', () => {
  let sessionId: string

  test.beforeEach(async ({ request }) => {
    // Create a session via API for the "two-sum" problem
    const res = await request.post('/api/sessions', {
      data: { problem_id: 'two-sum' },
    })
    expect(res.ok()).toBeTruthy()
    const session = await res.json()
    sessionId = session.id
  })

  test('loads problem description and code editor', async ({ page }) => {
    await page.goto(`/arena/${sessionId}`)

    // Problem title appears in top bar
    await expect(page.getByText('Two Sum')).toBeVisible({ timeout: 10_000 })

    // Difficulty badge
    await expect(page.getByText('easy')).toBeVisible()

    // Description and Results tab buttons
    await expect(page.getByRole('button', { name: 'Description' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Results' })).toBeVisible()

    // Code editor label
    await expect(page.getByText('solution.py')).toBeVisible()
  })

  test('can run code and see test results', async ({ page }) => {
    await page.goto(`/arena/${sessionId}`)
    await expect(page.getByText('Two Sum')).toBeVisible({ timeout: 10_000 })

    // Click "Run" button
    const runButton = page.getByRole('button', { name: /run/i })
    await expect(runButton).toBeVisible()
    await runButton.click()

    // Wait for execution response
    await page.waitForResponse(
      (res) => res.url().includes('/api/execute/run') && res.status() === 200,
      { timeout: 15_000 },
    )

    // Results tab should activate
    await expect(page.getByRole('button', { name: 'Results' })).toBeVisible()
  })

  test('can submit code and see interview button', async ({ page }) => {
    await page.goto(`/arena/${sessionId}`)
    await expect(page.getByText('Two Sum')).toBeVisible({ timeout: 10_000 })

    // Click "Submit" button
    const submitButton = page.getByRole('button', { name: /submit/i })
    await expect(submitButton).toBeVisible()
    await submitButton.click()

    // Wait for submit response
    await page.waitForResponse(
      (res) => res.url().includes('/api/execute/submit') && res.status() === 200,
      { timeout: 15_000 },
    )

    // "Start Interview" button should appear
    await expect(page.getByRole('button', { name: /start interview/i })).toBeVisible()
  })
})

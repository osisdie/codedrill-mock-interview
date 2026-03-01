import { test, expect } from '@playwright/test'

const SCREENSHOT_DIR = 'docs/screenshots'

// These tests call real AI APIs (OpenRouter) and stream responses,
// making them slow (~60s+). Skip in CI to keep the pipeline fast; run locally.
test.describe('Arena New Features — Show Answer, Chat, Ask AI', () => {
  test.skip(!!process.env.CI, 'Skipped in CI — requires AI API and runs long')

  let sessionId: string

  test.beforeEach(async ({ request }) => {
    const res = await request.post('/api/sessions', {
      data: { problem_id: 'fibonacci-number' },
    })
    expect(res.ok()).toBeTruthy()
    const session = await res.json()
    sessionId = session.id
  })

  test('Show Answer streams AI solution into the editor', async ({ page }) => {
    test.setTimeout(180_000)

    await page.goto(`/arena/${sessionId}`)
    await expect(page.getByRole('heading', { name: 'Fibonacci Number' })).toBeVisible({ timeout: 10_000 })

    // Wait for Monaco editor to mount before interacting (CDN loading can be slow)
    await page.waitForSelector('.monaco-editor', { timeout: 30_000 })

    // "Show Answer" button should be visible
    const showAnswerBtn = page.getByRole('button', { name: /show answer/i })
    await expect(showAnswerBtn).toBeVisible()

    // Click Show Answer — starts SSE streaming from the backend
    await showAnswerBtn.click()

    // "Stop" button should appear while streaming
    await expect(page.getByRole('button', { name: /stop/i })).toBeVisible({ timeout: 10_000 })

    // Wait for streaming to complete — Stop disappears, Show Answer reappears
    await expect(page.getByRole('button', { name: /show answer/i })).toBeVisible({ timeout: 150_000 })

    // Take screenshot of completed solution
    await page.screenshot({ path: `${SCREENSHOT_DIR}/feature-show-answer.png`, fullPage: false })

    // Editor should have substantial code content (solution streamed in)
    const textLength = await page.evaluate(() => {
      const lines = document.querySelector('.monaco-editor .view-lines')
      return lines?.textContent?.length || 0
    })
    expect(textLength).toBeGreaterThan(50)
  })

  test('Chat toggle opens and closes the chat panel', async ({ page }) => {
    await page.goto(`/arena/${sessionId}`)
    await expect(page.getByRole('heading', { name: 'Fibonacci Number' })).toBeVisible({ timeout: 10_000 })

    // Chat panel should NOT be open initially
    await expect(page.getByText('Ask questions about the code')).not.toBeVisible()

    // Click Chat toggle button
    const chatBtn = page.getByRole('button', { name: /^chat$/i })
    await expect(chatBtn).toBeVisible()
    await chatBtn.click()

    // Chat panel should now be visible with placeholder text
    await expect(page.getByText('Ask questions about the code')).toBeVisible({ timeout: 3_000 })

    // Chat input area should be visible
    const chatInput = page.getByPlaceholder(/ask about the code/i)
    await expect(chatInput).toBeVisible()

    // Send button should be visible
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible()

    // Take screenshot of chat panel open
    await page.screenshot({ path: `${SCREENSHOT_DIR}/feature-chat-panel.png`, fullPage: false })

    // Close the chat panel
    await chatBtn.click()
    await expect(page.getByText('Ask questions about the code')).not.toBeVisible()
  })

  test('Chat panel can send a message and receive AI response', async ({ page }) => {
    test.setTimeout(60_000)

    await page.goto(`/arena/${sessionId}`)
    await expect(page.getByRole('heading', { name: 'Fibonacci Number' })).toBeVisible({ timeout: 10_000 })

    // Open chat
    await page.getByRole('button', { name: /^chat$/i }).click()
    await expect(page.getByText('Ask questions about the code')).toBeVisible({ timeout: 3_000 })

    // Type a message
    const chatInput = page.getByPlaceholder(/ask about the code/i)
    await chatInput.fill('What approach should I use for Fibonacci Number?')

    // Click Send
    await page.getByRole('button', { name: /send/i }).click()

    // User message should appear in chat
    await expect(page.getByText('What approach should I use for Fibonacci Number?')).toBeVisible()

    // "Thinking..." indicator should appear
    await expect(page.getByText('Thinking...')).toBeVisible({ timeout: 3_000 })

    // Wait for AI response (timeout for API call)
    await expect(page.getByText('Thinking...')).not.toBeVisible({ timeout: 45_000 })

    // AI avatar should be present (there should be at least one AI message)
    const aiMessages = page.locator('span:text("AI")')
    await expect(aiMessages.first()).toBeVisible()

    // Take screenshot of chat with messages
    await page.screenshot({ path: `${SCREENSHOT_DIR}/feature-chat-conversation.png`, fullPage: false })
  })

  test('Ask AI button appears when text is selected in editor', async ({ page }) => {
    await page.goto(`/arena/${sessionId}`)
    await expect(page.getByRole('heading', { name: 'Fibonacci Number' })).toBeVisible({ timeout: 10_000 })

    // Wait for Monaco editor to load (CDN loading can be slow)
    await page.waitForSelector('.monaco-editor', { timeout: 30_000 })

    // The "Ask AI" button should NOT be visible when nothing is selected
    await expect(page.getByRole('button', { name: /ask ai/i })).not.toBeVisible()

    // Select text in the Monaco editor via keyboard shortcut (Ctrl+A to select all)
    await page.locator('.monaco-editor textarea').focus()
    await page.keyboard.press('Control+a')

    // "Ask AI" button should appear when text is selected
    await expect(page.getByRole('button', { name: /ask ai/i })).toBeVisible({ timeout: 3_000 })

    // Take screenshot showing Ask AI button
    await page.screenshot({ path: `${SCREENSHOT_DIR}/feature-ask-ai-selection.png`, fullPage: false })

    // Click "Ask AI" should open the chat panel
    await page.getByRole('button', { name: /ask ai/i }).click()
    await expect(page.getByPlaceholder(/ask about the code/i)).toBeVisible({ timeout: 3_000 })

    // The selected text indicator should be visible in chat header
    await expect(page.getByText(/Selected:/)).toBeVisible()
  })
})

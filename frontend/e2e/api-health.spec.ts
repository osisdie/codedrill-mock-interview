import { test, expect } from '@playwright/test'

test.describe('API Health', () => {
  test('backend health endpoint responds', async ({ request }) => {
    const res = await request.get('/api/health')
    expect(res.ok()).toBeTruthy()
    expect(await res.json()).toEqual({ status: 'ok' })
  })

  test('problems API returns problem list', async ({ request }) => {
    const res = await request.get('/api/problems')
    expect(res.ok()).toBeTruthy()

    const problems = await res.json()
    expect(Array.isArray(problems)).toBeTruthy()
    expect(problems.length).toBeGreaterThan(0)

    // Verify problem structure
    const first = problems[0]
    expect(first).toHaveProperty('id')
    expect(first).toHaveProperty('title')
    expect(first).toHaveProperty('category')
    expect(first).toHaveProperty('difficulty')
  })

  test('problems API supports category filter', async ({ request }) => {
    const res = await request.get('/api/problems?category=fastapi')
    expect(res.ok()).toBeTruthy()

    const problems = await res.json()
    for (const p of problems) {
      expect(p.category).toBe('fastapi')
    }
  })

  test('session CRUD workflow', async ({ request }) => {
    // Create
    const createRes = await request.post('/api/sessions', {
      data: { problem_id: 'two-sum' },
    })
    expect(createRes.ok()).toBeTruthy()
    const session = await createRes.json()
    expect(session.problem_id).toBe('two-sum')
    expect(session.status).toBe('in_progress')

    // Read
    const getRes = await request.get(`/api/sessions/${session.id}`)
    expect(getRes.ok()).toBeTruthy()
    const fetched = await getRes.json()
    expect(fetched.id).toBe(session.id)

    // Update
    const updateRes = await request.put(`/api/sessions/${session.id}`, {
      data: { code: 'def two_sum(nums, target): return []' },
    })
    expect(updateRes.ok()).toBeTruthy()
    const updated = await updateRes.json()
    expect(updated.code).toContain('two_sum')
  })
})

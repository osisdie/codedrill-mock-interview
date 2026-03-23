import { useMockApi } from '../demo/mockApi'

const DEMO = import.meta.env.VITE_DEMO_MODE === 'true'
const BASE = '/api'

const DEFAULT_TIMEOUT = 120_000 // 120s — generous for AI generation endpoints

async function request<T>(
  path: string,
  options?: RequestInit & { timeout?: number },
): Promise<T> {
  const { timeout = DEFAULT_TIMEOUT, ...fetchOptions } = options ?? {}

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)

  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...fetchOptions,
      signal: controller.signal,
    })
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(error.detail || res.statusText)
    }
    return res.json()
  } catch (e: any) {
    if (e.name === 'AbortError') {
      throw new Error('Request timed out — the AI service may be busy, please try again')
    }
    throw e
  } finally {
    clearTimeout(timer)
  }
}

export function useApi() {
  if (DEMO) return useMockApi()
  return {
    get: <T>(path: string, options?: { timeout?: number }) =>
      request<T>(path, options),
    post: <T>(path: string, body?: unknown, options?: { timeout?: number }) =>
      request<T>(path, { method: 'POST', body: JSON.stringify(body), ...options }),
    put: <T>(path: string, body?: unknown, options?: { timeout?: number }) =>
      request<T>(path, { method: 'PUT', body: JSON.stringify(body), ...options }),
  }
}

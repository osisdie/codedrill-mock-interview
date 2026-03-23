/**
 * Demo mode initialization.
 * Monkey-patches window.fetch to intercept SSE streaming URLs,
 * since CodingArenaView.vue calls fetch() directly (not through useApi).
 */
import { createMockSSEResponse } from './mockStream'

const SSE_PATTERN = /\/api\/problems\/([^/]+)\/solution\/stream/

const originalFetch = window.fetch.bind(window)

window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
  const match = url.match(SSE_PATTERN)
  if (match) {
    return createMockSSEResponse(match[1])
  }
  return originalFetch(input, init)
}

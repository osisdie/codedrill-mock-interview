/**
 * Mock SSE streaming for demo mode.
 * Simulates the /api/problems/{id}/solution/stream endpoint by emitting
 * pre-baked solution text character-by-character via a ReadableStream.
 */
import bundleData from './problems-bundle.json'

interface BundleProblem {
  id: string
  solution?: string
  [key: string]: unknown
}

const problems: BundleProblem[] = (bundleData as any).problems

/**
 * Creates a mock Response that mimics the SSE stream from the backend.
 * Compatible with the existing SSE parser in CodingArenaView.vue.
 */
export function createMockSSEResponse(problemId: string): Response {
  const problem = problems.find((p) => p.id === problemId)
  const solution = problem?.solution || '# No solution available for this problem in demo mode.'

  // Split into small chunks (~2-4 chars) to simulate streaming
  const chunks: string[] = []
  for (let i = 0; i < solution.length; i += 3) {
    chunks.push(solution.slice(i, i + 3))
  }

  const encoder = new TextEncoder()
  let index = 0

  const stream = new ReadableStream({
    async pull(controller) {
      if (index < chunks.length) {
        const data = JSON.stringify({ chunk: chunks[index] })
        controller.enqueue(encoder.encode(`data: ${data}\n\n`))
        index++
        // Small delay to simulate streaming
        await new Promise((r) => setTimeout(r, 8))
      } else {
        controller.enqueue(encoder.encode('data: [DONE]\n\n'))
        controller.close()
      }
    },
  })

  return new Response(stream, {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  })
}

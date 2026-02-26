import { ref } from 'vue'

// Python keywords/patterns that start a new logical block.
// Typing pauses before these so the reader can absorb context.
const BLOCK_STARTERS = [
  'def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ',
  'try:', 'except', 'finally:', 'with ', 'return ', 'raise ',
  'import ', 'from ', '#',
]

export function useTypewriter() {
  const isTyping = ref(false)
  const displayedText = ref('')

  let cancelRequested = false
  let activeTimer: ReturnType<typeof setTimeout> | null = null
  let pendingResolve: (() => void) | null = null
  let fullTextRef = ''
  let onUpdateRef: ((text: string, lineCount: number) => void) | null = null

  /**
   * Check if the line starting at `pos` in `text` begins with a block keyword
   * (after stripping leading whitespace).
   */
  function isBlockStart(text: string, lineStartPos: number): boolean {
    let i = lineStartPos
    while (i < text.length && text[i] === ' ') i++
    const rest = text.slice(i)
    return BLOCK_STARTERS.some((kw) => rest.startsWith(kw))
  }

  /**
   * Calculate delay for the current character based on context.
   *
   * Timing strategy:
   *   - Newline before a block-start line: 400ms (pause to think)
   *   - Newline before a blank line:       200ms (section break)
   *   - Regular newline:                   100ms
   *   - Inside a comment (#):               35ms (slower, reader follows)
   *   - Normal code character:              18ms (fluid typing)
   */
  function getCharDelay(
    char: string,
    fullText: string,
    pos: number,
  ): number {
    if (char === '\n') {
      const nextLineStart = pos + 1
      if (nextLineStart >= fullText.length) return 100

      if (fullText[nextLineStart] === '\n') return 200
      if (isBlockStart(fullText, nextLineStart)) return 400

      return 100
    }

    const lastNewline = fullText.lastIndexOf('\n', pos - 1)
    const lineStart = lastNewline + 1
    const linePrefix = fullText.slice(lineStart, pos + 1)
    if (linePrefix.trimStart().startsWith('#')) return 35

    return 18
  }

  /**
   * Type text character by character using setTimeout chain.
   * Uses an iterative setTimeout approach (not async loop) so the browser
   * event loop has idle time between each step — important for Playwright
   * and DevTools interactions during the animation.
   */
  function typeText(
    fullText: string,
    onUpdate: (text: string, lineCount: number) => void,
  ): Promise<void> {
    return new Promise<void>((resolve) => {
      isTyping.value = true
      cancelRequested = false
      displayedText.value = ''
      fullTextRef = fullText
      onUpdateRef = onUpdate
      pendingResolve = resolve

      let pos = 0
      let lineCount = 1
      let lastFlushTime = 0
      const FLUSH_INTERVAL = 50

      function step() {
        if (cancelRequested || pos >= fullText.length) {
          if (!cancelRequested) {
            // Natural completion — final flush
            onUpdate(displayedText.value, lineCount)
          }
          activeTimer = null
          isTyping.value = false
          pendingResolve = null
          resolve()
          return
        }

        displayedText.value += fullText[pos]
        if (fullText[pos] === '\n') lineCount++

        const delay = getCharDelay(fullText[pos], fullText, pos)
        const now = performance.now()

        // Throttle DOM updates to avoid overwhelming Monaco/Vue
        if (now - lastFlushTime >= FLUSH_INTERVAL || fullText[pos] === '\n' || delay >= 100) {
          onUpdate(displayedText.value, lineCount)
          lastFlushTime = now
        }

        pos++
        activeTimer = setTimeout(step, delay)
      }

      // Start the chain
      step()
    })
  }

  function cancel() {
    cancelRequested = true
    if (activeTimer) {
      clearTimeout(activeTimer)
      activeTimer = null
    }
    // Show full text immediately
    if (fullTextRef && onUpdateRef) {
      displayedText.value = fullTextRef
      const totalLines = fullTextRef.split('\n').length
      onUpdateRef(fullTextRef, totalLines)
    }
    isTyping.value = false
    // Resolve the pending promise so the caller continues
    if (pendingResolve) {
      const r = pendingResolve
      pendingResolve = null
      r()
    }
  }

  return { isTyping, displayedText, typeText, cancel }
}

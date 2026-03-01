<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import { useMonaco } from '@guolao/vue-monaco-editor'
import { useProblemStore } from '../stores/problemStore'
import { useSessionStore } from '../stores/sessionStore'
import { useTimerStore } from '../stores/timerStore'
import TimerDisplay from '../components/arena/TimerDisplay.vue'
import TestCasesPanel from '../components/arena/TestCasesPanel.vue'
import RunSubmitBar from '../components/arena/RunSubmitBar.vue'
import CodeChat from '../components/arena/CodeChat.vue'
import type { SubmissionResult } from '../types'

const { monacoRef } = useMonaco()

const route = useRoute()
const router = useRouter()
const problemStore = useProblemStore()
const sessionStore = useSessionStore()
const timer = useTimerStore()
const code = ref('')
const testResults = ref<SubmissionResult[]>([])
const activeTab = ref<'description' | 'results'>('description')
const editorRef = ref<any>(null)
const streamPreRef = ref<HTMLDivElement | null>(null)
const solutionLoading = ref(false)
const completedHtml = ref('')  // HTML for fully-typed lines (append-only, no flicker)
const typingHtml = ref('')     // HTML for the line currently being typed char-by-char
const chatOpen = ref(false)
const selectedText = ref<string | null>(null)

const sessionId = route.params.sessionId as string

onMounted(async () => {
  await sessionStore.fetchSession(sessionId)
  const session = sessionStore.currentSession
  if (!session) return

  await problemStore.fetchProblem(session.problem_id)
  code.value = session.code

  if (session.time_remaining_seconds && session.status === 'in_progress') {
    timer.start(session.time_remaining_seconds)
  }
})

onUnmounted(() => {
  timer.stop()
})

// Auto-save code on change (debounced) — skip during streaming
let saveTimeout: ReturnType<typeof setTimeout> | null = null
watch(code, (newCode) => {
  if (solutionLoading.value) return  // don't auto-save partial streaming code
  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(() => {
    sessionStore.updateSession(sessionId, {
      code: newCode,
      time_remaining_seconds: timer.remaining,
    })
  }, 1500)
})

async function handleRun() {
  // Save code first
  await sessionStore.updateSession(sessionId, { code: code.value })
  const result = await sessionStore.runCode(sessionId)
  testResults.value = result.results
  activeTab.value = 'results'
}

async function handleSubmit() {
  await sessionStore.updateSession(sessionId, { code: code.value })
  timer.stop()
  const result = await sessionStore.submitCode(sessionId)
  testResults.value = result.results
  activeTab.value = 'results'
}

function goToInterview() {
  router.push({ name: 'interview', params: { sessionId } })
}

function handleEditorMount(editor: any) {
  editorRef.value = editor
  // Track text selection changes in the editor
  editor.onDidChangeCursorSelection(() => {
    const selection = editor.getSelection()
    if (selection && !selection.isEmpty()) {
      selectedText.value = editor.getModel()?.getValueInRange(selection) || null
    } else {
      selectedText.value = null
    }
  })
}

function toggleChat() {
  chatOpen.value = !chatOpen.value
}

function askAboutSelection() {
  chatOpen.value = true
}

let streamAbort: AbortController | null = null
let twTimer: ReturnType<typeof setTimeout> | null = null
let visibleTextBuffer = ''      // plain text of completed lines (for Stop button)
let currentTypingPartial = ''   // partial text of line being typed (for Stop button)

// Strip leading ```python / trailing ``` fences the AI sometimes adds
function stripFences(text: string): string {
  let s = text
  if (s.startsWith('```python\n')) s = s.slice(10)
  else if (s.startsWith('```python')) s = s.slice(9)
  else if (s.startsWith('```\n')) s = s.slice(4)
  else if (s.startsWith('```')) s = s.slice(3)
  if (s.endsWith('\n```')) s = s.slice(0, -4)
  else if (s.endsWith('```')) s = s.slice(0, -3)
  return s
}

// Content-aware delay for typewriter effect
function typewriterDelay(line: string): number {
  const trimmed = line.trim()
  if (trimmed === '') return 120                       // blank line — pause
  if (trimmed.startsWith('#')) return 80               // comment
  if (trimmed.startsWith('def ') || trimmed.startsWith('class ')) return 90
  if (trimmed.endsWith(':')) return 70                  // block opener
  if (/[.;,!?]$/.test(trimmed)) return 60              // punctuation
  return 40                                            // regular code
}

// Colorize text using Monaco's tokenizer (returns HTML string)
async function colorizeText(text: string): Promise<string> {
  const monaco = monacoRef.value
  if (!monaco || !text) return escapeHtml(text)
  try {
    return await monaco.editor.colorize(text, 'python', { tabSize: 4 })
  } catch {
    return escapeHtml(text)
  }
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

async function handleShowAnswer() {
  const problemId = problemStore.currentProblem?.id
  if (!problemId) return

  solutionLoading.value = true
  completedHtml.value = ''
  typingHtml.value = ''
  visibleTextBuffer = ''
  currentTypingPartial = ''
  streamAbort = new AbortController()

  // Pending lines queue: SSE fills this, typewriter loop drains it
  const pendingLines: string[] = []
  let sseComplete = false
  let rawBuffer = ''

  // ── Char-by-char typewriter ──────────────────────────
  function startTypewriter(): Promise<void> {
    return new Promise<void>((resolve) => {
      let currentLine = ''
      let charIdx = 0
      let lineComplete = true  // start true to pick up first line

      async function tick() {
        // Pick up next line when current is done
        if (lineComplete) {
          if (pendingLines.length === 0) {
            if (sseComplete) { twTimer = null; resolve(); return }
            twTimer = setTimeout(tick, 30)  // poll for more lines
            return
          }
          currentLine = pendingLines.shift()!
          charIdx = 0
          lineComplete = false

          // Blank lines: add immediately, no typing needed
          if (currentLine === '') {
            visibleTextBuffer += (visibleTextBuffer ? '\n' : '')
            completedHtml.value += '<div style="min-height:1.2em"></div>'
            lineComplete = true
            twTimer = setTimeout(tick, 80)
            return
          }
        }

        // Type characters within the current line
        const isComment = currentLine.trim().startsWith('#')
        const chunkSize = isComment ? 1 : 2
        charIdx = Math.min(charIdx + chunkSize, currentLine.length)
        currentTypingPartial = currentLine.slice(0, charIdx)

        // Colorize partial line for typing display
        typingHtml.value = await colorizeText(currentTypingPartial)

        // Scroll to keep content centered
        if (streamPreRef.value) {
          const el = streamPreRef.value
          el.style.paddingBottom = `${Math.floor(el.clientHeight / 2)}px`
          el.scrollTop = el.scrollHeight
        }

        if (charIdx >= currentLine.length) {
          // Line fully typed — move to completed section (append-only, no flicker)
          visibleTextBuffer += (visibleTextBuffer ? '\n' : '') + currentLine
          completedHtml.value += typingHtml.value  // reuse already-colorized HTML
          typingHtml.value = ''
          currentTypingPartial = ''
          lineComplete = true
          twTimer = setTimeout(tick, typewriterDelay(currentLine))
        } else {
          // Continue typing within line
          twTimer = setTimeout(tick, isComment ? 25 : 16)
        }
      }
      twTimer = setTimeout(tick, 40)
    })
  }

  // ── SSE reader ────────────────────────────────────────
  async function readSSE() {
    try {
      const res = await fetch(`/api/problems/${problemId}/solution/stream`, {
        signal: streamAbort!.signal,
      })
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let sseBuffer = ''
      let streamDone = false
      let prevStripped = ''

      while (!streamDone) {
        const { done, value } = await reader.read()
        if (done) break

        sseBuffer += decoder.decode(value, { stream: true })
        const sseLines = sseBuffer.split('\n')
        sseBuffer = sseLines.pop()!

        for (const sseLine of sseLines) {
          if (!sseLine.startsWith('data: ')) continue
          const payload = sseLine.slice(6).trim()
          if (payload === '[DONE]') {
            streamDone = true
            break
          }
          try {
            const { chunk, error } = JSON.parse(payload)
            if (error) throw new Error(error)
            if (chunk) rawBuffer += chunk
          } catch { /* skip malformed SSE frames */ }
        }

        // Strip fences and enqueue any new complete lines
        const stripped = stripFences(rawBuffer)
        if (stripped.length > prevStripped.length) {
          const newText = stripped.slice(prevStripped.length)
          const newLines = newText.split('\n')
          if (!stripped.endsWith('\n') && !streamDone) {
            const partial = newLines.pop()!
            prevStripped = stripped.slice(0, stripped.length - partial.length)
          } else {
            prevStripped = stripped
            // "text\n".split('\n') → ["text", ""] — drop trailing empty artifact
            if (newLines.length > 0 && newLines[newLines.length - 1] === '') {
              newLines.pop()
            }
          }
          for (const nl of newLines) {
            pendingLines.push(nl)
          }
        }
      }

      // Enqueue any remaining partial line
      const finalStripped = stripFences(rawBuffer)
      const remaining = finalStripped.slice(prevStripped.length)
      if (remaining) {
        const parts = remaining.split('\n')
        // Drop trailing empty artifact from split
        if (parts.length > 0 && parts[parts.length - 1] === '') parts.pop()
        for (const nl of parts) {
          pendingLines.push(nl)
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        if (!rawBuffer) {
          pendingLines.push(`# Error fetching solution: ${e.message}`)
        }
      }
    } finally {
      sseComplete = true
    }
  }

  // Start both concurrently: SSE fills the queue, typewriter drains it
  const twPromise = startTypewriter()
  await readSSE()
  await twPromise

  // Transfer final text to Monaco editor
  code.value = stripFences(rawBuffer).trim() + '\n'
  streamAbort = null
  completedHtml.value = ''
  typingHtml.value = ''
  visibleTextBuffer = ''
  currentTypingPartial = ''
  solutionLoading.value = false
}

function handleStopTyping() {
  if (streamAbort) {
    streamAbort.abort()
    streamAbort = null
  }
  if (twTimer) {
    clearTimeout(twTimer)
    twTimer = null
  }
  // Keep whatever has been typed so far — use tracked plain text, not DOM extraction
  let text = visibleTextBuffer
  if (currentTypingPartial) {
    text += (text ? '\n' : '') + currentTypingPartial
  }
  const trimmed = text.trim()
  code.value = trimmed ? trimmed + '\n' : ''
  completedHtml.value = ''
  typingHtml.value = ''
  visibleTextBuffer = ''
  currentTypingPartial = ''
  solutionLoading.value = false
}
</script>

<template>
  <div class="h-[calc(100vh-4rem)] flex flex-col">
    <!-- Top bar -->
    <div class="flex items-center justify-between px-4 py-2 bg-surface-light border-b border-surface-lighter">
      <div class="flex items-center gap-4">
        <h2 class="text-lg font-semibold text-white">
          {{ problemStore.currentProblem?.title ?? 'Loading...' }}
        </h2>
        <span
          v-if="problemStore.currentProblem"
          class="px-2 py-0.5 rounded-full text-xs font-semibold capitalize"
          :class="{
            'bg-easy/20 text-easy': problemStore.currentProblem.difficulty === 'easy',
            'bg-medium/20 text-medium': problemStore.currentProblem.difficulty === 'medium',
            'bg-hard/20 text-hard': problemStore.currentProblem.difficulty === 'hard',
          }"
        >
          {{ problemStore.currentProblem.difficulty }}
        </span>
      </div>
      <div class="flex items-center gap-4">
        <TimerDisplay />
        <RunSubmitBar
          :executing="sessionStore.executing"
          :submitted="sessionStore.currentSession?.status === 'submitted'"
          @run="handleRun"
          @submit="handleSubmit"
        />
        <button
          v-if="sessionStore.currentSession?.status === 'submitted'"
          @click="goToInterview"
          class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Start Interview
        </button>
      </div>
    </div>

    <!-- Split panels -->
    <Splitpanes class="flex-1">
      <!-- Left: Problem description + test results -->
      <Pane :size="40" :min-size="25">
        <div class="h-full flex flex-col overflow-hidden">
          <div class="flex border-b border-surface-lighter">
            <button
              @click="activeTab = 'description'"
              class="px-4 py-2 text-sm font-medium transition-colors"
              :class="activeTab === 'description' ? 'text-white border-b-2 border-primary-500' : 'text-gray-400 hover:text-white'"
            >
              Description
            </button>
            <button
              @click="activeTab = 'results'"
              class="px-4 py-2 text-sm font-medium transition-colors"
              :class="activeTab === 'results' ? 'text-white border-b-2 border-primary-500' : 'text-gray-400 hover:text-white'"
            >
              Results
              <span v-if="testResults.length" class="ml-1 text-xs">
                ({{ testResults.filter(r => r.passed).length }}/{{ testResults.length }})
              </span>
            </button>
          </div>

          <!-- Description tab -->
          <div v-show="activeTab === 'description'" class="flex-1 overflow-y-auto p-4 space-y-4">
            <template v-if="problemStore.currentProblem">
              <div class="prose prose-invert prose-sm max-w-none">
                <p class="whitespace-pre-wrap text-gray-300">{{ problemStore.currentProblem.description }}</p>
              </div>

              <div v-for="(ex, i) in problemStore.currentProblem.examples" :key="i"
                class="bg-surface-lighter rounded-lg p-3 space-y-1">
                <div class="text-xs font-semibold text-gray-400">Example {{ i + 1 }}</div>
                <div class="font-mono text-sm text-gray-300">
                  <div><span class="text-gray-500">Input:</span> {{ ex.input }}</div>
                  <div><span class="text-gray-500">Output:</span> {{ ex.output }}</div>
                  <div v-if="ex.explanation" class="text-gray-400 text-xs mt-1">{{ ex.explanation }}</div>
                </div>
              </div>

              <div>
                <h4 class="text-sm font-semibold text-gray-300 mb-2">Constraints</h4>
                <ul class="text-sm text-gray-400 space-y-1">
                  <li v-for="c in problemStore.currentProblem.constraints" :key="c" class="font-mono text-xs">
                    {{ c }}
                  </li>
                </ul>
              </div>
            </template>
          </div>

          <!-- Results tab -->
          <div v-show="activeTab === 'results'" class="flex-1 overflow-y-auto p-4">
            <TestCasesPanel :results="testResults" :loading="sessionStore.executing" />
          </div>
        </div>
      </Pane>

      <!-- Right: Code editor + Chat -->
      <Pane :size="60" :min-size="30">
        <div class="h-full flex flex-col">
          <div class="px-4 py-2 bg-surface-light border-b border-surface-lighter text-sm text-gray-400 flex items-center justify-between">
            <span>solution.py</span>
            <div class="flex items-center gap-2">
              <!-- Ask AI about selection -->
              <button
                v-if="selectedText && !chatOpen"
                @click="askAboutSelection"
                class="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium rounded-md transition-colors flex items-center gap-1"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                Ask AI
              </button>
              <!-- Chat toggle -->
              <button
                @click="toggleChat"
                class="px-3 py-1 text-xs font-medium rounded-md transition-colors flex items-center gap-1"
                :class="chatOpen
                  ? 'bg-primary-600 text-white'
                  : 'bg-surface-lighter text-gray-300 hover:text-white'"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
                Chat
              </button>
              <!-- Stop streaming -->
              <button
                v-if="solutionLoading"
                @click="handleStopTyping"
                class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-md transition-colors flex items-center gap-1"
              >
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 16 16"><rect x="3" y="3" width="10" height="10" rx="1"/></svg>
                Stop
              </button>
              <!-- Show Answer -->
              <button
                v-if="!solutionLoading"
                @click="handleShowAnswer"
                :disabled="solutionLoading || !problemStore.currentProblem"
                class="px-3 py-1 text-xs font-medium rounded-md transition-colors flex items-center gap-1"
                :class="solutionLoading
                  ? 'bg-gray-600 text-gray-400 cursor-wait'
                  : 'bg-amber-600 hover:bg-amber-700 text-white'"
              >
                <svg v-if="solutionLoading" class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
                {{ solutionLoading ? 'Generating...' : 'Show Answer' }}
              </button>
            </div>
          </div>
          <!-- Editor + Chat vertical split -->
          <Splitpanes horizontal class="flex-1">
            <Pane :size="chatOpen ? 60 : 100" :min-size="30">
              <!-- During streaming: split overlay (completed lines are stable, only typing line updates) -->
              <div
                v-if="solutionLoading"
                ref="streamPreRef"
                class="h-full overflow-auto bg-[#1e1e1e] text-[#d4d4d4] font-mono text-sm p-3 m-0"
              >
                <div v-html="completedHtml"></div>
                <div v-html="typingHtml"></div>
                <span v-if="!completedHtml && !typingHtml" style="color:#888">Generating solution...</span>
              </div>
              <vue-monaco-editor
                v-else
                v-model:value="code"
                language="python"
                theme="vs-dark"
                :options="{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  insertSpaces: true,
                  wordWrap: 'on',
                  padding: { top: 12 },
                }"
                @mount="handleEditorMount"
              />
            </Pane>
            <Pane v-if="chatOpen" :size="40" :min-size="20">
              <CodeChat
                :problem-id="problemStore.currentProblem?.id ?? ''"
                :code="code"
                :selected-text="selectedText"
              />
            </Pane>
          </Splitpanes>
        </div>
      </Pane>
    </Splitpanes>
  </div>
</template>

<style>
.splitpanes__splitter {
  background-color: #1e293b;
}
.splitpanes--vertical > .splitpanes__splitter {
  width: 4px !important;
}
.splitpanes--horizontal > .splitpanes__splitter {
  height: 4px !important;
}
.splitpanes__splitter:hover {
  background-color: #3b82f6;
}
</style>

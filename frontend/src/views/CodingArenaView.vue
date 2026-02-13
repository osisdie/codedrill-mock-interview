<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import { useProblemStore } from '../stores/problemStore'
import { useSessionStore } from '../stores/sessionStore'
import { useTimerStore } from '../stores/timerStore'
import TimerDisplay from '../components/arena/TimerDisplay.vue'
import TestCasesPanel from '../components/arena/TestCasesPanel.vue'
import RunSubmitBar from '../components/arena/RunSubmitBar.vue'
import type { SubmissionResult } from '../types'

const route = useRoute()
const router = useRouter()
const problemStore = useProblemStore()
const sessionStore = useSessionStore()
const timer = useTimerStore()

const code = ref('')
const testResults = ref<SubmissionResult[]>([])
const activeTab = ref<'description' | 'results'>('description')
const editorRef = ref<any>(null)

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

// Auto-save code on change (debounced)
let saveTimeout: ReturnType<typeof setTimeout> | null = null
watch(code, (newCode) => {
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

      <!-- Right: Code editor -->
      <Pane :size="60" :min-size="30">
        <div class="h-full flex flex-col">
          <div class="px-4 py-2 bg-surface-light border-b border-surface-lighter text-sm text-gray-400">
            solution.py
          </div>
          <div class="flex-1">
            <vue-monaco-editor
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
          </div>
        </div>
      </Pane>
    </Splitpanes>
  </div>
</template>

<style>
.splitpanes__splitter {
  background-color: #1e293b;
  width: 4px !important;
}
.splitpanes__splitter:hover {
  background-color: #3b82f6;
}
</style>

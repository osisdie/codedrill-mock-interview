<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/sessionStore'
import DifficultyBadge from '../components/problems/DifficultyBadge.vue'

const router = useRouter()
const sessionStore = useSessionStore()

onMounted(async () => {
  await sessionStore.fetchSessions()
})

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function statusBadge(status: string) {
  switch (status) {
    case 'in_progress': return { label: 'In Progress', class: 'bg-blue-900/30 text-blue-400' }
    case 'submitted': return { label: 'Submitted', class: 'bg-yellow-900/30 text-yellow-400' }
    case 'scored': return { label: 'Scored', class: 'bg-green-900/30 text-green-400' }
    default: return { label: status, class: 'bg-gray-800 text-gray-400' }
  }
}

function navigateToSession(session: any) {
  if (session.status === 'scored') {
    router.push({ name: 'score', params: { sessionId: session.id } })
  } else if (session.status === 'submitted') {
    router.push({ name: 'interview', params: { sessionId: session.id } })
  } else {
    router.push({ name: 'arena', params: { sessionId: session.id } })
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-white mb-8">Session History</h1>

    <div v-if="sessionStore.loading" class="text-center py-20 text-gray-400">
      Loading sessions...
    </div>

    <div v-else-if="sessionStore.sessions.length === 0" class="text-center py-20">
      <p class="text-gray-500 text-lg">No sessions yet.</p>
      <button
        @click="router.push({ name: 'problems' })"
        class="mt-4 px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        Start Practicing
      </button>
    </div>

    <div v-else class="space-y-3">
      <button
        v-for="session in sessionStore.sessions"
        :key="session.id"
        @click="navigateToSession(session)"
        class="w-full text-left bg-surface-light rounded-lg border border-surface-lighter p-4 hover:border-primary-500/50 transition-colors"
      >
        <div class="flex items-center justify-between">
          <div>
            <div class="text-white font-medium">{{ session.problem_id }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ formatDate(session.started_at) }}</div>
          </div>
          <div class="flex items-center gap-3">
            <span v-if="session.score" class="text-lg font-bold"
              :class="session.score.overall_score >= 80 ? 'text-green-400' : session.score.overall_score >= 60 ? 'text-yellow-400' : 'text-red-400'"
            >
              {{ session.score.overall_score }}
            </span>
            <span
              class="px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="statusBadge(session.status).class"
            >
              {{ statusBadge(session.status).label }}
            </span>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

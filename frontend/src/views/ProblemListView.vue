<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProblemStore } from '../stores/problemStore'
import { useSessionStore } from '../stores/sessionStore'
import ProblemCard from '../components/problems/ProblemCard.vue'

const route = useRoute()
const router = useRouter()
const problemStore = useProblemStore()
const sessionStore = useSessionStore()

const selectedCategory = ref<string>((route.params.category as string) || '')
const selectedDifficulty = ref('')

const categories = [
  { value: '', label: 'All' },
  { value: 'algorithms', label: 'Algorithms' },
  { value: 'fastapi', label: 'FastAPI' },
  { value: 'django', label: 'Django' },
  { value: 'pytest', label: 'Pytest' },
]

const difficulties = [
  { value: '', label: 'All' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
]

async function loadProblems() {
  await problemStore.fetchProblems(
    selectedCategory.value || undefined,
    selectedDifficulty.value || undefined,
  )
}

async function startProblem(problemId: string) {
  const session = await sessionStore.createSession(problemId)
  router.push({ name: 'arena', params: { sessionId: session.id } })
}

watch([selectedCategory, selectedDifficulty], loadProblems)
onMounted(loadProblems)
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-white mb-8">Problems</h1>

    <!-- Filters -->
    <div class="flex flex-wrap gap-4 mb-8">
      <div class="flex gap-2">
        <button
          v-for="cat in categories"
          :key="cat.value"
          @click="selectedCategory = cat.value"
          class="px-3 py-1.5 text-sm rounded-lg font-medium transition-colors"
          :class="selectedCategory === cat.value
            ? 'bg-primary-600 text-white'
            : 'bg-surface-light text-gray-400 hover:text-white'"
        >
          {{ cat.label }}
        </button>
      </div>
      <div class="flex gap-2">
        <button
          v-for="d in difficulties"
          :key="d.value"
          @click="selectedDifficulty = d.value"
          class="px-3 py-1.5 text-sm rounded-lg font-medium transition-colors"
          :class="selectedDifficulty === d.value
            ? 'bg-primary-600 text-white'
            : 'bg-surface-light text-gray-400 hover:text-white'"
        >
          {{ d.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="problemStore.loading" class="text-center py-20 text-gray-400">
      Loading problems...
    </div>

    <!-- Problem Grid -->
    <div v-else-if="problemStore.problems.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <ProblemCard
        v-for="problem in problemStore.problems"
        :key="problem.id"
        :problem="problem"
        @start="startProblem"
      />
    </div>

    <!-- Empty -->
    <div v-else class="text-center py-20 text-gray-500">
      No problems found for the selected filters.
    </div>
  </div>
</template>

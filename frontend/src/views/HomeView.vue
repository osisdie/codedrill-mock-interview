<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const categories = [
  {
    id: 'algorithms',
    title: 'Algorithms',
    description: 'Classic LeetCode-style problems to sharpen your problem-solving skills. Practice array manipulation, dynamic programming, and more.',
    icon: '&#x1F9E9;',
    color: 'from-blue-600 to-blue-800',
    count: '10 problems',
  },
  {
    id: 'fastapi',
    title: 'FastAPI',
    description: 'Build REST APIs, handle validation, middleware, authentication, and dependency injection with FastAPI.',
    icon: '&#x26A1;',
    color: 'from-emerald-600 to-emerald-800',
    count: '5 problems',
  },
  {
    id: 'django',
    title: 'Django',
    description: 'Master Django ORM queries, class-based views, DRF serializers, signals, and middleware.',
    icon: '&#x1F3D7;&#xFE0F;',
    color: 'from-purple-600 to-purple-800',
    count: '5 problems',
  },
]

function navigateToCategory(categoryId: string) {
  router.push({ name: 'problems-category', params: { category: categoryId } })
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Hero -->
    <div class="text-center mb-16">
      <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4">
        Sharpen Your Coding Skills
      </h1>
      <p class="text-lg text-gray-400 max-w-2xl mx-auto">
        Solve real coding problems, get AI-powered mock interviews, and receive detailed scored feedback — all in one platform.
      </p>
    </div>

    <!-- Category Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="navigateToCategory(cat.id)"
        class="group relative overflow-hidden rounded-xl p-6 text-left transition-all duration-300 hover:scale-105 hover:shadow-2xl"
        :class="`bg-gradient-to-br ${cat.color}`"
      >
        <div class="text-4xl mb-4" v-html="cat.icon"></div>
        <h2 class="text-2xl font-bold text-white mb-2">{{ cat.title }}</h2>
        <p class="text-sm text-white/80 mb-4 line-clamp-3">{{ cat.description }}</p>
        <span class="inline-block text-xs font-medium bg-white/20 text-white px-3 py-1 rounded-full">
          {{ cat.count }}
        </span>
        <div class="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      </button>
    </div>

    <!-- How It Works -->
    <div class="mt-20 max-w-4xl mx-auto">
      <h2 class="text-2xl font-bold text-white text-center mb-10">How It Works</h2>
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-6">
        <div v-for="(step, i) in [
          { icon: '&#x1F4CB;', label: 'Pick a Problem' },
          { icon: '&#x1F4BB;', label: 'Write Code' },
          { icon: '&#x1F916;', label: 'AI Interview' },
          { icon: '&#x1F4CA;', label: 'Get Scored' },
        ]" :key="i" class="text-center">
          <div class="w-14 h-14 mx-auto rounded-full bg-surface-light flex items-center justify-center text-2xl mb-3" v-html="step.icon"></div>
          <p class="text-sm text-gray-300 font-medium">{{ step.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

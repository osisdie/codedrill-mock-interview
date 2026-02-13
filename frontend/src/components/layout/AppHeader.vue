<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="bg-surface-light border-b border-surface-lighter">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <RouterLink to="/" class="flex items-center gap-2 text-xl font-bold text-white hover:text-primary-400 transition-colors">
          <span class="text-2xl">&#x1F3AF;</span>
          <span>CodeDrill</span>
        </RouterLink>
        <nav class="flex items-center gap-6">
          <RouterLink
            to="/problems"
            class="text-gray-300 hover:text-white transition-colors text-sm font-medium"
            active-class="text-primary-400"
          >
            Problems
          </RouterLink>
          <RouterLink
            to="/history"
            class="text-gray-300 hover:text-white transition-colors text-sm font-medium"
            active-class="text-primary-400"
          >
            History
          </RouterLink>
        </nav>
      </div>
    </div>
  </header>
</template>

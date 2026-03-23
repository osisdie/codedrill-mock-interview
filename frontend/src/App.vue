<script setup lang="ts">
import AppHeader from './components/layout/AppHeader.vue'

const isDemo = import.meta.env.VITE_DEMO_MODE === 'true'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <div
      v-if="isDemo"
      class="bg-amber-500/90 text-amber-950 text-center text-sm py-1.5 px-4 font-medium"
    >
      Demo Mode —
      <a
        href="https://github.com/osisdie/codedrill-mock-interview"
        target="_blank"
        class="underline hover:text-amber-800"
      >
        Clone the repo
      </a>
      for full AI interview + code execution features
    </div>
    <AppHeader />
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

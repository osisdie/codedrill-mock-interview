import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTimerStore = defineStore('timer', () => {
  const remaining = ref(0)
  const isRunning = ref(false)
  let interval: ReturnType<typeof setInterval> | null = null

  const formatted = computed(() => {
    const m = Math.floor(remaining.value / 60)
    const s = remaining.value % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  })

  const isLow = computed(() => remaining.value > 0 && remaining.value <= 60)
  const isExpired = computed(() => remaining.value <= 0 && isRunning.value)

  function start(seconds: number) {
    remaining.value = seconds
    isRunning.value = true
    if (interval) clearInterval(interval)
    interval = setInterval(() => {
      if (remaining.value > 0) {
        remaining.value--
      } else {
        stop()
      }
    }, 1000)
  }

  function stop() {
    isRunning.value = false
    if (interval) {
      clearInterval(interval)
      interval = null
    }
  }

  function reset(seconds: number) {
    stop()
    remaining.value = seconds
  }

  return { remaining, isRunning, formatted, isLow, isExpired, start, stop, reset }
})

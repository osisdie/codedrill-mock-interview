import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

const isDemo = process.env.VITE_DEMO_MODE === 'true'

export default defineConfig({
  base: isDemo ? '/codedrill-mock-interview/' : '/',
  plugins: [vue(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: parseInt(process.env.PORT || '5573', 10),
    // Use polling for file watching on WSL2 + Windows filesystem (/mnt/c)
    watch: {
      usePolling: true,
      interval: 1000,
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8573',
        changeOrigin: true,
        // Disable proxy buffering for SSE streaming endpoints
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
              proxyRes.headers['cache-control'] = 'no-cache'
              proxyRes.headers['x-accel-buffering'] = 'no'
            }
          })
        },
      },
    },
  },
})

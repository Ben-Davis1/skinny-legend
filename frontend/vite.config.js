import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    host: true
  },
  preview: {
    host: true,
    port: 4173,
    strictPort: false,
    allowedHosts: ['skinny-legend.onrender.com', '.onrender.com']
  },
  build: {
    outDir: 'dist'
  }
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",   // ✅ THIS FIXES IT
    setupFiles: './src/test/setup.js', 
  },
  plugins: [react()],
})

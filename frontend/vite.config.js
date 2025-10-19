import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Production optimizations
    target: 'es2015',
    minify: 'esbuild', // Use esbuild (default, faster than terser)
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor chunks for better caching
          'react-vendor': ['react', 'react-dom'],
          'markdown-vendor': ['react-markdown'],
          'socket-vendor': ['socket.io-client'],
          'state-vendor': ['zustand'],
        },
      },
    },
    // Enable gzip compression hint
    reportCompressedSize: true,
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000,
  },
  // Enable source maps for production debugging
  sourcemap: true,
})

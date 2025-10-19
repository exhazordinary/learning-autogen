import { defineConfig, mergeConfig } from 'vite'
import { defineConfig as defineVitestConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import viteConfig from './vite.config.js'

export default mergeConfig(
  viteConfig,
  defineVitestConfig({
    test: {
      globals: true,
      environment: 'happy-dom',
      setupFiles: './src/test/setup.js',
      css: true,
      environmentOptions: {
        happyDOM: {
          settings: {
            disableJavaScriptEvaluation: false,
            disableJavaScriptFileLoading: false,
          },
        },
      },
    },
  })
)

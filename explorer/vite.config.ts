import react from '@vitejs/plugin-react'
import { readFileSync } from 'node:fs'
import { defineConfig } from 'vitest/config'
import { serveFiles } from './tools/serve-files/index.ts'

const constants = JSON.parse(readFileSync(new URL('./contract/schema/constants.json', import.meta.url), 'utf8')) as {
  HOST: string
  APP_PORT: number
}

export default defineConfig({
  // Relative base: the build works from / and from any sub-path of a static host.
  base: './',
  plugins: [react(), serveFiles()],
  // The bundle is served by tools/serve-files, never copied into dist.
  publicDir: false,
  server: { host: constants.HOST, port: constants.APP_PORT, strictPort: true },
  preview: { host: constants.HOST, port: constants.APP_PORT, strictPort: true },
  build: {
    target: 'es2022',
    chunkSizeWarningLimit: 1500,
    // HOSTED_ENTRY: build another html entry (used only by the hosted-build check to prove the mechanics)
    ...(process.env.HOSTED_ENTRY ? { rollupOptions: { input: process.env.HOSTED_ENTRY } } : {}),
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}', 'tools/**/*.test.ts', 'scripts/**/*.test.ts'],
    css: false,
  },
})

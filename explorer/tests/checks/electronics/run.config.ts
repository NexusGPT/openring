// Local runner for the electronics checks: npx playwright test -c tests/checks/electronics/run.config.ts
import { defineConfig } from '@playwright/test'
import { chromiumPath } from '../../support'

const executablePath = chromiumPath()
export default defineConfig({
  testDir: '.',
  testMatch: '*.spec.ts',
  outputDir: '../../../test-results/electronics',
  workers: 1,
  timeout: 120_000,
  reporter: [['list']],
  use: {
    headless: true,
    viewport: { width: 1512, height: 982 },
    launchOptions: { ...(executablePath ? { executablePath } : {}), args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] },
  },
})

// Local runner for the look checks only: npx playwright test -c tests/checks/look/run.config.ts [-g look-C03]
// The specs start their own app on 8809 (one at a time); stop anything on that port first.
import { defineConfig } from '@playwright/test'
import { chromiumPath } from '../../support'

const executablePath = chromiumPath()
export default defineConfig({
  testDir: '.',
  testMatch: '*.spec.ts',
  outputDir: '../../../test-results/look',
  workers: 1,
  timeout: 120_000,
  reporter: [['list']],
  use: {
    headless: true,
    viewport: { width: 1512, height: 982 },
    launchOptions: { ...(executablePath ? { executablePath } : {}), args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] },
  },
})

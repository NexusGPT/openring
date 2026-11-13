// Local runner for the home checks only: the same settings as tests/playwright.config.ts, project `checks`,
// without the journey web server (these specs start their own apps). Use: npx playwright test -c tests/checks/home/run.config.ts
import { defineConfig } from '@playwright/test'
import { chromiumPath } from '../../support'

const executablePath = chromiumPath()
export default defineConfig({
  testDir: '.',
  testMatch: '*.spec.ts',
  outputDir: '../../../test-results/behaviour',
  workers: 1,
  timeout: 90_000,
  reporter: [['list']],
  use: {
    headless: true,
    viewport: { width: 1512, height: 982 },
    launchOptions: { ...(executablePath ? { executablePath } : {}), args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] },
  },
})

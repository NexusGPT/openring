// Local runner for the open-files checks only (they start their own apps). Use:
//   npx playwright test -c tests/checks/open-files/run.config.ts
import { defineConfig } from '@playwright/test'
import { chromiumPath } from '../../support'

const executablePath = chromiumPath()
export default defineConfig({
  testDir: '.',
  testMatch: '*.spec.ts',
  outputDir: '../../../test-results/open-files',
  workers: 1,
  timeout: 90_000,
  reporter: [['list']],
  use: {
    headless: true,
    viewport: { width: 1512, height: 982 },
    launchOptions: { ...(executablePath ? { executablePath } : {}), args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] },
  },
})

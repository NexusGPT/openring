// Headless only. Uses the Chromium the project already has; downloads nothing.
//   support   ./support/*.spec.ts, the self-check of the shared test support (needs no server)
//   static    ./static/hosted.spec.ts, the built folder served by a plain static server under /ring/
//   journeys  ../journeys/*.spec.ts  on JOURNEY_PORT, against the fixture bundle
//   checks    ./checks, ./seams, ./smoke   on APP_PORT, against the bundle named by EXPLORER_BUNDLE
import { defineConfig } from '@playwright/test'
import { APP_PORT, HOST, JOURNEY_PORT } from '../src/contract/constants'
import { FIXTURE_DATA, FIXTURE_SOURCE, chromiumPath } from './support'

const executablePath = chromiumPath()
const use = {
  headless: true,
  viewport: { width: 1512, height: 982 },
  launchOptions: {
    ...(executablePath ? { executablePath } : {}),
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  },
}

export default defineConfig({
  testDir: '.',
  outputDir: '../test-results',
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  projects: [
    {
      name: 'support',
      testDir: './support',
      testMatch: '*.spec.ts',
      use,
    },
    {
      name: 'static',
      testDir: './static',
      testMatch: '*.spec.ts',
      timeout: 120_000,
      use,
    },
    {
      name: 'journeys',
      testDir: '../journeys',
      use: { ...use, baseURL: `http://${HOST}:${JOURNEY_PORT}` },
      metadata: { port: JOURNEY_PORT },
    },
    {
      name: 'checks',
      testDir: '.',
      testMatch: ['checks/**/*.spec.ts', 'seams/**/*.spec.ts', 'smoke/**/*.spec.ts'],
      use: { ...use, baseURL: `http://${HOST}:${APP_PORT}` },
    },
  ],
  webServer: [
    {
      command: `npx vite --port ${JOURNEY_PORT} --strictPort`,
      url: `http://${HOST}:${JOURNEY_PORT}/`,
      cwd: '..',
      reuseExistingServer: false,
      env: { EXPLORER_BUNDLE: process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA, EXPLORER_SOURCE: process.env.EXPLORER_SOURCE ?? FIXTURE_SOURCE },
      timeout: 60_000,
    },
  ],
})

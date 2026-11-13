// Shared helpers for journeys and checks. Headless only; nothing here opens a window.
import type { Locator, Page } from '@playwright/test'
import { ROUTES, testId, type RouteId, type TestScope } from '../../src/contract/ids'

export const ROUTE_PATH: Record<RouteId, string> = {
  home: '/',
  look: '/look',
  inside: '/inside',
  electronics: '/electronics',
  board: '/board',
  parts: '/parts',
  behaviour: '/behaviour',
  case: '/case',
  open: '/open',
}
export const ALL_ROUTES: readonly RouteId[] = ROUTES

/** Element by the '<route>.<element>' grammar. */
export function byTestId(page: Page, scope: TestScope, element: string): Locator {
  return page.getByTestId(testId(scope, element))
}
/** Element by suffix, for a shared component hosted on any route (e.g. every '.part-card'). */
export function bySuffix(page: Page, element: string): Locator {
  return page.locator(`[data-testid$=".${element}"]`)
}

export interface Watch {
  errors: string[]
  /** requests that left 127.0.0.1 (blocked when blockOffline was used) */
  external: string[]
}

/** Collect console errors, uncaught page errors and failed local requests. */
export function watchConsole(page: Page): Watch {
  const w: Watch = { errors: [], external: [] }
  page.on('console', (m) => {
    if (m.type() === 'error') w.errors.push(`console: ${m.text()}`)
  })
  page.on('pageerror', (e) => w.errors.push(`pageerror: ${e.message}`))
  page.on('response', (r) => {
    if (r.status() >= 400) w.errors.push(`http ${r.status()}: ${r.url()}`)
  })
  page.on('requestfailed', (r) => {
    if (!w.external.includes(r.url())) w.errors.push(`requestfailed: ${r.url()}`)
  })
  return w
}

/** Abort every request whose host is not 127.0.0.1: the app must work with no network. */
export async function blockOffline(page: Page, w: Watch): Promise<void> {
  await page.route('**/*', (route) => {
    const u = new URL(route.request().url())
    if (u.hostname === '127.0.0.1' || u.protocol === 'data:' || u.protocol === 'blob:') return route.continue()
    w.external.push(route.request().url())
    return route.abort()
  })
}

export async function waitStageReady(page: Page, timeoutMs = 30_000): Promise<void> {
  await page.waitForFunction(() => window.__stage?.ready === true, undefined, { timeout: timeoutMs })
}

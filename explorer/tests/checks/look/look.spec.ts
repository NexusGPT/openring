// look-C01..C11: the Look screen on the LIVE bundle, on made bundles (3 open options, one picked, all rejected,
// no look-options record) and on an EMPTY one. Headless; 127.0.0.1 only. One app at a time on 8809; it stops only what it started.
// Option texts and finish colours come from the bundle being served; none is written in src.
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import { bannerText } from '../../../src/contract/vocabulary'
import type { LookOptions, RingModel } from '../../../src/contract/records'
import { bundleEnv, byTestId, emptyBundle, startApp, waitStageReady, watchConsole, type RunningApp } from '../../support'
import { LIVE, SIX, makeBundle, ringOf, type Made } from './bundles'

const lookIndex = (dir: string): LookOptions | null => {
  try {
    return JSON.parse(readFileSync(join(dir, 'looks', 'index.json'), 'utf8')) as LookOptions
  } catch {
    return null
  }
}
// an absent record is a 404 on /data/ (data layer, not the screen); a console line for it carries no url
const stageErrors = (errs: string[]) => errs.filter((e) => !e.includes('/data/') && !/Failed to load resource.*404/.test(e))

// One app at a time on 8809 (the port this lane owns); a case's app starts when a test first asks for it.
interface Case {
  bundle: string
  source?: string
  made?: Made
}
const cases: Record<string, Case> = {}
let running: { name: string; app: RunningApp } | null = null
const ensure = async (name: string): Promise<RunningApp> => {
  if (running?.name === name) return running.app
  await running?.app.stop()
  running = null
  await new Promise((r) => setTimeout(r, 400))
  const c = cases[name]!
  running = { name, app: await startApp({ port: 8809, env: bundleEnv(c.bundle, c.source) }) }
  return running.app
}
const add = (name: string, made: Made) => (cases[name] = { bundle: made.dir, source: made.source, made })
test.beforeAll(() => {
  cases.live = { bundle: LIVE }
  add('three', makeBundle(SIX))
  add('picked', makeBundle(SIX, 'b'))
  add('none', makeBundle(SIX.map((o) => ({ ...o, rejected: true }))))
  cases.empty = { bundle: emptyBundle() }
  add('mixed', makeBundle([{ id: 'z', title: 'Look Z: OPEN', in_design: true }, { id: 'y', title: 'Look Y: REJECTED', rejected: true }]))
  add('fallback', makeBundle(null))
})
test.afterAll(async () => {
  await running?.app.stop()
  for (const c of Object.values(cases)) c.made?.cleanup()
})

const open = async (page: Page, name: string, stage = true) => {
  const app = await ensure(name)
  await page.goto(app.url + '/look')
  await page.waitForSelector('[data-testid="look.panel"]')
  if (stage) await waitStageReady(page)
}
const panel = (page: Page) => byTestId(page, 'app', 'panel')
const options = (page: Page) => panel(page).locator('[data-testid="look.look-option"]')
const sw = (page: Page, group: string, value: string) => panel(page).locator(`[data-testid="look.${group}"][data-value="${value}"]`)
const ringOfCase = (name: string): RingModel => ringOf(name === 'live' ? LIVE : cases[name]!.made!.dir)

test('look-C01 live bundle: one panel per open option of looks/index.json, rejected never; exterior state sentence shown', async ({ page }) => {
  const w = watchConsole(page)
  await open(page, 'live')
  const idx = lookIndex(LIVE)
  const shown = (idx?.options ?? []).filter((o) => !o.rejected && (!idx?.picked || o.id === idx.picked))
  if (idx) {
    await expect(options(page)).toHaveCount(shown.length)
    for (const o of shown) await expect(panel(page).locator(`[data-testid="look.look-option"][data-option="${o.id}"]`)).toContainText(o.title)
    for (const o of (idx.options ?? []).filter((x) => x.rejected)) await expect(panel(page)).not.toContainText(o.title)
  } else await expect(options(page)).toHaveCount(1) // no look-options record yet: the ring-model's exterior stands in
  const st = ringOfCase('live').exterior.status
  if (st === 'in-design') await expect(panel(page).locator('[data-kind="exterior-in-design"]')).toHaveText(bannerText({ kind: 'exterior-in-design' }).replace(/\s+/g, ' '), { useInnerText: true })
  expect(stageErrors(w.errors)).toEqual([])
})

test('look-C02 finish: every option takes the finish colour; aria-pressed follows', async ({ page }) => {
  await open(page, 'three')
  await expect(options(page)).toHaveCount(SIX.length)
  const finishes = cases.three!.made!.looks.finishes
  const second = finishes[1]!
  await expect(sw(page, 'finish', finishes[0]!.name)).toHaveAttribute('aria-pressed', 'true')
  await sw(page, 'finish', second.name).click()
  await expect(sw(page, 'finish', second.name)).toHaveAttribute('aria-pressed', 'true')
  await expect(sw(page, 'finish', finishes[0]!.name)).toHaveAttribute('aria-pressed', 'false')
  for (const o of SIX) {
    await expect.poll(() => page.evaluate((id) => window.__stage?.material(id, 'body')?.color?.toLowerCase() ?? null, o.id), { timeout: 15_000 }).toBe(second.colour.toLowerCase())
  }
})

test('look-C03 view: "On a finger" shows the finger on every option; the pressed value follows', async ({ page }) => {
  await open(page, 'three')
  await expect(sw(page, 'view', 'three-quarter')).toHaveAttribute('aria-pressed', 'true')
  await sw(page, 'view', 'finger').click()
  await expect(sw(page, 'view', 'finger')).toHaveAttribute('aria-pressed', 'true')
  await expect(sw(page, 'view', 'three-quarter')).toHaveAttribute('aria-pressed', 'false')
  for (const o of SIX) await expect.poll(() => page.evaluate((id) => window.__stage?.fingerVisible(id) ?? false, o.id)).toBe(true)
  await expect.poll(() => page.evaluate(() => window.__stage?.preset())).toBe('finger')
  await sw(page, 'view', 'top').click()
  for (const o of SIX) await expect.poll(() => page.evaluate((id) => window.__stage?.fingerVisible(id) ?? true, o.id)).toBe(false)
})

test('look-C04 screen: a state lights the labelled fields; Off draws none', async ({ page }) => {
  await open(page, 'three')
  const states = ringOfCase('three').screens.states
  const second = states[1]!
  await sw(page, 'screen', second.state).click()
  await expect(sw(page, 'screen', second.state)).toHaveAttribute('aria-pressed', 'true')
  await expect.poll(() => page.evaluate(() => window.__stage?.screenFields() ?? [])).toEqual(second.fields.map((f) => f.label))
  await sw(page, 'screen', 'off').click()
  await expect(sw(page, 'screen', 'off')).toHaveAttribute('aria-pressed', 'true')
  await expect.poll(() => page.evaluate(() => window.__stage?.screenFields() ?? ['x'])).toEqual([])
})

test('look-C05 one option picked: it alone renders, labelled Picked', async ({ page }) => {
  await open(page, 'picked')
  await expect(options(page)).toHaveCount(1)
  await expect(options(page).first()).toHaveAttribute('data-option', 'b')
  await expect(options(page).first()).toContainText('Picked')
  await expect(options(page).first()).toContainText(SIX[1]!.title)
})

test('look-C06 every option rejected: no panel, one banner "New options in design"', async ({ page }) => {
  await open(page, 'none')
  await expect(options(page)).toHaveCount(0)
  const banner = panel(page).locator('[data-testid="look.state-banner"]')
  await expect(banner).toHaveCount(1)
  await expect(banner).toContainText('New options in design')
  for (const o of SIX) await expect(panel(page)).not.toContainText(o.title)
})

test('look-C07 a rejected option beside an open one is never shown; the open one has title, sentence, trade-offs, Details', async ({ page }) => {
  await open(page, 'mixed', false)
  await expect(options(page)).toHaveCount(1)
  const o = options(page).first()
  await expect(o).toContainText('Look Z: OPEN')
  await expect(o).toContainText('Made-up sentence')
  await expect(o).toContainText('made-up trade-off one')
  await expect(panel(page)).not.toContainText('Look Y: REJECTED')
  const d = o.locator('details')
  await expect(d).not.toHaveAttribute('open', '')
  await d.locator('summary').click()
  await expect(d).toHaveAttribute('open', '')
  await expect(d).toContainText('design/look/test/notes.md')
})

test('look-C08 empty bundle: one honest banner, no switches, no uncaught error', async ({ page }) => {
  const w = watchConsole(page)
  await open(page, 'empty', false)
  const banner = panel(page).locator('[data-testid="look.state-banner"]')
  await expect(banner).toHaveCount(1)
  await expect(banner).toContainText('Not built yet')
  await expect(options(page)).toHaveCount(0)
  await expect(byTestId(page, 'look', 'switches')).toHaveCount(0)
  expect(stageErrors(w.errors)).toEqual([])
})

test('look-C09 no look-options record: the ring-model exterior stands in, in design, never as approved', async ({ page }) => {
  await open(page, 'fallback')
  await expect(options(page)).toHaveCount(1)
  await expect(options(page).first()).toHaveAttribute('data-fallback', 'true')
  await expect(options(page).first()).not.toContainText('Picked')
  await expect(panel(page).locator('[data-kind="exterior-in-design"]')).toHaveCount(1)
  await expect(sw(page, 'view', 'finger')).toBeVisible()
})

test('look-C10 no page scroll at 1512x982 and 1280x800; the panel scrolls inside itself', async ({ page }) => {
  for (const name of ['live', 'three']) {
    for (const size of [{ width: 1512, height: 982 }, { width: 1280, height: 800 }]) {
      await page.setViewportSize(size)
      await open(page, name, false)
      const m = await page.evaluate(() => ({ h: document.documentElement.scrollHeight, w: document.documentElement.scrollWidth, ih: innerHeight, iw: innerWidth }))
      expect(m.h, `${name} ${size.width}`).toBeLessThanOrEqual(m.ih)
      expect(m.w, `${name} ${size.width}`).toBeLessThanOrEqual(m.iw)
    }
  }
})

test('look-C11 reduced motion: switches change without a transition', async ({ browser }) => {
  const ctx = await browser.newContext({ reducedMotion: 'reduce', viewport: { width: 1512, height: 982 } })
  const page = await ctx.newPage()
  await open(page, 'three', false)
  const dur = await sw(page, 'view', 'top').evaluate((el) => getComputedStyle(el).transitionDuration)
  expect(Math.max(...dur.split(',').map((s) => parseFloat(s)))).toBeLessThan(0.001)
  await ctx.close()
})

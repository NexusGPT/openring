// behaviour-C01..C10: the Behaviour screen on the LIVE bundle and on an EMPTY one. Headless; 127.0.0.1 only.
// Each run starts its own apps (live on 8831, empty on 8832) and stops only what it started.
// Every state name, label and number is read from the bundle on disk; none is written here.
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import type { FirmwareRules } from '../../../src/contract/records'
import { initialState } from '../../../src/engine/behaviour'
import { EXPLORER_ROOT, bundleEnv, byTestId, emptyBundle, startApp, waitStageReady, watchConsole, type RunningApp } from '../../support'

const LIVE = join(EXPLORER_ROOT, 'public', 'data')
const rules = JSON.parse(readFileSync(join(LIVE, 'behaviour.json'), 'utf8')) as FirmwareRules
const label = (id: string) => rules.states.find((s) => s.id === id)!.label
const REST = initialState(rules)
const longG = rules.gestures.find((g) => g.kind === 'long_press')!
const HOLD = longG.min_hold_ms!
const startRec = rules.transitions.find((t) => t.from === REST && t.event_kind === 'long_press')!
const REC = startRec.to
const patternMarks = (ids: string[]) => ids.reduce((n, id) => n + rules.motor_patterns.find((m) => m.id === id)!.pulses.length, 0)

let live: RunningApp
let empty: RunningApp
test.beforeAll(async () => {
  live = await startApp({ port: 8831, env: bundleEnv(LIVE) })
  empty = await startApp({ port: 8832, env: bundleEnv(emptyBundle()) })
})
test.afterAll(async () => {
  await live?.stop()
  await empty?.stop()
})

const open = async (page: Page, app: RunningApp) => {
  await page.goto(app.url + '/behaviour')
  await page.waitForSelector('[data-testid="behaviour.panel"]')
}
const openLive = async (page: Page) => {
  await open(page, live)
  await page.waitForSelector('[data-testid="behaviour.state"]')
  await waitStageReady(page)
}
const state = (page: Page) => byTestId(page, 'behaviour', 'state')
const holdMouse = async (page: Page, ms: number) => {
  const b = (await byTestId(page, 'behaviour', 'joystick-centre').boundingBox())!
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2)
  await page.mouse.down()
  await page.waitForTimeout(ms)
  await page.mouse.up()
}

test('behaviour-C01 at rest: the state label equals the bundle, light off, no timer', async ({ page }) => {
  await openLive(page)
  await expect(state(page)).toHaveText(label(REST))
  await expect(state(page)).toHaveAttribute('data-state-id', REST)
  await expect(byTestId(page, 'behaviour', 'light')).toHaveAttribute('data-on', 'false')
  await expect(byTestId(page, 'behaviour', 'timer')).not.toHaveText(/\d\d:\d\d:\d\d/)
  expect(await page.evaluate(() => window.__stage?.lightOn())).toBe(false)
})

test('behaviour-C02 a held mouse press starts the recording: label, light, stage light, 1 vibration mark, timer runs', async ({ page }) => {
  await openLive(page)
  await holdMouse(page, HOLD + 150)
  await expect(state(page)).toHaveText(label(REC))
  await expect(byTestId(page, 'behaviour', 'light')).toHaveAttribute('data-on', 'true')
  await expect.poll(() => page.evaluate(() => window.__stage?.lightOn())).toBe(true)
  await expect(byTestId(page, 'behaviour', 'vibration-mark')).toHaveCount(patternMarks(startRec.motor_ids))
  const t0 = await byTestId(page, 'behaviour', 'timer').textContent()
  await expect.poll(() => byTestId(page, 'behaviour', 'timer').textContent(), { timeout: 2500 }).not.toBe(t0)
})

test('behaviour-C03 Space held for the same time does the same', async ({ page }) => {
  await openLive(page)
  await page.keyboard.down('Space')
  await page.waitForTimeout(HOLD + 150)
  await page.keyboard.up('Space')
  await expect(state(page)).toHaveText(label(REC))
  await expect.poll(() => page.evaluate(() => window.__stage?.lightOn())).toBe(true)
})

test('behaviour-C04 a hold shorter than the long press changes nothing', async ({ page }) => {
  await openLive(page)
  const short = rules.gestures.find((g) => g.kind === 'short_press')!
  await holdMouse(page, short.max_hold_ms! + 100)
  await page.waitForTimeout(short.window_ms! + 200)
  await expect(state(page)).toHaveText(label(REST))
  await expect(byTestId(page, 'behaviour', 'vibration-mark')).toHaveCount(0)
})

test('behaviour-C05 while recording a tap adds one highlight and keeps the state; a second hold stops it', async ({ page }) => {
  await openLive(page)
  await holdMouse(page, HOLD + 150)
  await expect(state(page)).toHaveText(label(REC))
  const short = rules.gestures.find((g) => g.kind === 'short_press')!
  await holdMouse(page, 200)
  await page.waitForTimeout(short.window_ms! + 250)
  await expect(byTestId(page, 'behaviour', 'highlight-mark')).toHaveCount(1)
  await expect(byTestId(page, 'behaviour', 'highlights')).toHaveAttribute('data-count', '1')
  await expect(state(page)).toHaveText(label(REC))
  await holdMouse(page, HOLD + 150)
  await expect(state(page)).toHaveText(label(REST))
  await expect(byTestId(page, 'behaviour', 'light')).toHaveAttribute('data-on', 'false')
})

test('behaviour-C06 the progress ring fills during the hold', async ({ page }) => {
  await openLive(page)
  const b = (await byTestId(page, 'behaviour', 'joystick-centre').boundingBox())!
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2)
  await page.mouse.down()
  await page.waitForTimeout(HOLD / 2)
  const half = Number(await byTestId(page, 'behaviour', 'hold-progress').getAttribute('data-frac'))
  await page.mouse.up()
  expect(half).toBeGreaterThan(0.3)
  expect(half).toBeLessThan(0.8)
})

test('behaviour-C07 a held press on the joystick of the 3D ring starts the recording; a short drag from it only turns the ring', async ({ page }) => {
  await openLive(page)
  const stage = (await byTestId(page, 'app', 'stage').boundingBox())!
  // the ring turns by itself until the first drag: drag once on empty space, then read the button's place
  await page.mouse.move(stage.x + 40, stage.y + 60)
  await page.mouse.down()
  await page.mouse.move(stage.x + 90, stage.y + 60, { steps: 6 })
  await page.mouse.up()
  await expect.poll(() => page.evaluate(() => window.__stage?.autoRotate)).toBe(false)
  const at = async () => {
    const p = await page.evaluate(() => window.__stage?.screenPos('joystick') ?? null)
    const c = (await page.locator('[data-testid="app.stage"] canvas').first().boundingBox())!
    return p ? { x: c.x + p.x, y: c.y + p.y } : null
  }
  const p1 = await at()
  expect(p1).not.toBeNull()
  // drag starting on the button: no press
  await page.mouse.move(p1!.x, p1!.y)
  await page.mouse.down()
  await page.mouse.move(p1!.x + 60, p1!.y + 5, { steps: 6 })
  await page.waitForTimeout(HOLD + 200)
  await page.mouse.up()
  await expect(state(page)).toHaveText(label(REST))
  const p2 = await at()
  await page.mouse.move(p2!.x, p2!.y)
  await page.mouse.down()
  await page.waitForTimeout(HOLD + 200)
  await page.mouse.up()
  await expect(state(page)).toHaveText(label(REC))
})

test('behaviour-C08 the state list shows every state of the bundle with exactly one marked', async ({ page }) => {
  await openLive(page)
  const rows = byTestId(page, 'behaviour', 'state-item')
  await expect(rows).toHaveCount(rules.states.length)
  await expect(page.locator('[data-testid="behaviour.state-item"][data-current="true"]')).toHaveCount(1)
  await expect(page.locator(`[data-testid="behaviour.state-item"][data-current="true"]`)).toHaveAttribute('data-state-id', REST)
})

test('behaviour-C09 stale rules: the contract sentence and the content stays, dimmed', async ({ page }) => {
  await openLive(page)
  const manifest = JSON.parse(readFileSync(join(LIVE, 'manifest.json'), 'utf8'))
  const e = manifest.records['firmware-rules']
  if (e.status !== 'stale') test.skip(true, 'the live bundle is not stale')
  const b = byTestId(page, 'app', 'panel').getByTestId('behaviour.state-banner')
  await expect(b).toHaveAttribute('data-kind', 'stale')
  await expect(b).toContainText(`Made for design ${e.basis_version}; the design is now ${e.current_version}.`)
  await expect(page.locator('[data-testid="behaviour.panel"] [data-dimmed="true"]')).toHaveCount(1)
  await expect(state(page)).toBeVisible()
})

test('behaviour-C10 empty bundle: one banner with the command, 0 console errors, no controls, no page scroll', async ({ page }) => {
  const w = watchConsole(page)
  await open(page, empty)
  // the stage draws its own banner with the same id in the stage area: count the panel's only
  const banner = byTestId(page, 'app', 'panel').getByTestId('behaviour.state-banner')
  await expect(banner).toHaveCount(1)
  await expect(banner).toHaveAttribute('data-kind', 'missing')
  await expect(banner.locator('code')).toHaveText('npm run collect')
  await expect(byTestId(page, 'behaviour', 'joystick-centre')).toHaveCount(0)
  const real = w.errors.filter((e) => !/http 404: .*\/data\//.test(e) && !/Failed to load resource.*404/.test(e))
  expect(real).toEqual([])
  expect(await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)).toBeLessThanOrEqual(0)
})

test('behaviour-C11 no page scroll at 1512x982, 1440x900 and 1280x800', async ({ page }) => {
  for (const [w, h] of [[1512, 982], [1440, 900], [1280, 800]] as const) {
    await page.setViewportSize({ width: w, height: h })
    await open(page, live)
    await page.waitForSelector('[data-testid="behaviour.state"]')
    expect(await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)).toBeLessThanOrEqual(0)
  }
})

test('behaviour-C12 the seconds handed to the ring screen equal the panel timer', async ({ page }) => {
  await openLive(page)
  await holdMouse(page, HOLD + 150)
  await expect(state(page)).toHaveText(label(REC))
  await page.waitForTimeout(2300)
  for (let i = 0; i < 3; i++) {
    const [txt, passed] = await page.evaluate(() => [
      document.querySelector('[data-testid="behaviour.timer"]')!.textContent!,
      document.querySelector('[data-testid="behaviour.panel"]')!.getAttribute('data-stage-elapsed')!,
    ])
    const [h, m, sec] = txt.split(':').map(Number)
    expect(Number(passed)).toBe(h! * 3600 + m! * 60 + sec!)
    expect(Number(passed)).toBeGreaterThanOrEqual(2)
    await page.waitForTimeout(700)
  }
})

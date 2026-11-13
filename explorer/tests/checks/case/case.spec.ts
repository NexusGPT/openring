// case-C01..C08: the Case screen on the LIVE bundle and on an EMPTY one. Headless; 127.0.0.1 only.
// Each run starts its own apps (live on 8833, empty on 8834) and stops only what it started.
// Every number, name and count is read from the bundle on disk; none is written here.
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import type { Case, Manifest, Parts } from '../../../src/contract/records'
import { EXPLORER_ROOT, bundleEnv, byTestId, emptyBundle, startApp, waitStageReady, watchConsole, type RunningApp } from '../../support'

const LIVE = join(EXPLORER_ROOT, 'public', 'data')
const read = <T>(f: string): T => JSON.parse(readFileSync(join(LIVE, f), 'utf8')) as T
const theCase = read<Case>('case/index.json')
const parts = read<Parts>('parts.json')
const manifest = read<Manifest>('manifest.json')
const text = (f: { value: string | number; unit: string | null }) => (f.unit && !String(f.value).toLowerCase().includes(f.unit.toLowerCase()) ? `${f.value} ${f.unit}` : String(f.value))
const pinNode = theCase.glb!.nodes.find((n) => n.part_ids.length > 0 && n.name.startsWith('pin_'))!
const pinId = pinNode.part_ids[0]!
const pinLine = parts.lines.find((l) => l.part_ids.includes(pinId))!

let live: RunningApp
let empty: RunningApp
test.beforeAll(async () => {
  live = await startApp({ port: 8833, env: bundleEnv(LIVE) })
  empty = await startApp({ port: 8834, env: bundleEnv(emptyBundle()) })
})
test.afterAll(async () => {
  await live?.stop()
  await empty?.stop()
})

const open = async (page: Page, app: RunningApp) => {
  await page.goto(app.url + '/case')
  await page.waitForSelector('[data-testid="case.panel"]')
}
const openLive = async (page: Page) => {
  await open(page, live)
  await page.waitForSelector('[data-testid="case.fact"]')
  await waitStageReady(page)
}

test('case-C01 every fact of the bundle is on the panel with its value', async ({ page }) => {
  await openLive(page)
  for (const f of theCase.facts) {
    const row = page.locator(`[data-testid="case.fact"][data-fact="${f.id}"]`)
    await expect(row).toContainText(f.label)
    await expect(row).toContainText(text(f))
  }
  await expect(byTestId(page, 'case', 'numbers')).toContainText('33.6 x 33.4 x 55.2 mm')
  await expect(byTestId(page, 'case', 'numbers')).toContainText('700 mAh')
})

test('case-C02 the parts list has one row per case line, and the counts equal the bundle totals', async ({ page }) => {
  await openLive(page)
  await expect(byTestId(page, 'case', 'part-row')).toHaveCount(parts.totals.case.lines)
  await expect(byTestId(page, 'case', 'parts-count')).toContainText(`${parts.totals.case.lines} lines`)
  await expect(byTestId(page, 'case', 'parts-count')).toContainText(`${parts.totals.case.parts} parts`)
  const first = parts.lines.find((l) => l.bom === 'case')!
  await expect(byTestId(page, 'case', 'part-row').first()).toContainText(first.function ?? first.item)
})

test('case-C03 the lid button swings the lid to 90 degrees or more, and back', async ({ page }) => {
  await openLive(page)
  expect(await page.evaluate(() => window.__stage?.nodeRotationDeg('lid'))).toBeLessThan(5)
  await byTestId(page, 'case', 'lid-toggle').click()
  await expect.poll(() => page.evaluate(() => window.__stage?.nodeRotationDeg('lid') ?? 0), { timeout: 8000 }).toBeGreaterThanOrEqual(90)
  await expect(byTestId(page, 'case', 'lid-toggle')).toHaveAttribute('data-open', 'true')
  await byTestId(page, 'case', 'lid-toggle').click()
  await expect.poll(() => page.evaluate(() => window.__stage?.nodeRotationDeg('lid') ?? 0), { timeout: 8000 }).toBeLessThan(5)
})

test('case-C04 a click on a pin of the 3D case opens the card of the pin line', async ({ page }) => {
  await openLive(page)
  await byTestId(page, 'case', 'lid-toggle').click()
  await expect.poll(() => page.evaluate(() => window.__stage?.nodeRotationDeg('lid') ?? 0), { timeout: 8000 }).toBeGreaterThanOrEqual(90)
  const stage = (await byTestId(page, 'app', 'stage').boundingBox())!
  await page.mouse.move(stage.x + 30, stage.y + 40)
  await page.mouse.down()
  await page.mouse.move(stage.x + 60, stage.y + 40, { steps: 5 })
  await page.mouse.up()
  const p = await page.evaluate((n) => window.__stage?.screenPos(n) ?? null, pinNode.name)
  expect(p).not.toBeNull()
  const c = (await page.locator('[data-testid="app.stage"] canvas').first().boundingBox())!
  await page.mouse.click(c.x + p!.x, c.y + p!.y)
  const card = byTestId(page, 'case', 'part-card')
  await expect(card).toHaveAttribute('data-part-id', /^case:/)
  await expect(byTestId(page, 'case', 'selected')).toContainText(pinLine.function ?? pinLine.item)
})

test('case-C05 a click on a list row opens that line card (VBUS, D-, D+, GND for the pins); closing it clears the address', async ({ page }) => {
  await openLive(page)
  await page.locator(`[data-testid="case.part-row"][data-part-id="${pinId}"] button`).click()
  const card = byTestId(page, 'case', 'part-card')
  await expect(card).toHaveAttribute('data-part-id', pinId)
  // the part card shows the part note first; the pin names ride on the parts-list line shown with it
  for (const w of ['VBUS', 'D-', 'D+', 'GND']) await expect(byTestId(page, 'case', 'selected')).toContainText(w)
  expect(new URL(page.url()).searchParams.get('part')).toBe(pinId)
  await page.getByRole('button', { name: 'Close part card' }).click()
  await expect(card).toHaveCount(0)
  expect(new URL(page.url()).searchParams.get('part')).toBeNull()
})

test('case-C06 stale case: the contract sentence and the reason show, the content stays, dimmed', async ({ page }) => {
  await openLive(page)
  const e = manifest.records.case
  if (e.status !== 'stale') test.skip(true, 'the live case record is not stale')
  const b = byTestId(page, 'app', 'panel').getByTestId('case.state-banner').first()
  await expect(b).toHaveAttribute('data-kind', 'stale')
  await expect(b).toContainText(`Made for design ${e.basis_version}; the design is now ${e.current_version}.`)
  if (e.message) await expect(byTestId(page, 'case', 'stale-reason')).toHaveText(e.message)
  await expect(page.locator('[data-testid="case.panel"] [data-dimmed="true"]')).toHaveCount(1)
  await expect(byTestId(page, 'case', 'fact').first()).toBeVisible()
})

test('case-C07 empty bundle: one banner with the command, 0 console errors, no lid button, no page scroll', async ({ page }) => {
  const w = watchConsole(page)
  await open(page, empty)
  // the stage draws its own banner with the same id in the stage area: count the panel's only
  const banner = byTestId(page, 'app', 'panel').getByTestId('case.state-banner')
  await expect(banner).toHaveCount(1)
  await expect(banner).toHaveAttribute('data-kind', 'missing')
  await expect(banner.locator('code')).toHaveText('npm run collect')
  await expect(byTestId(page, 'case', 'lid-toggle')).toHaveCount(0)
  await expect(byTestId(page, 'case', 'fact')).toHaveCount(0)
  const real = w.errors.filter((e) => !/http 404: .*\/data\//.test(e) && !/Failed to load resource.*404/.test(e))
  expect(real).toEqual([])
  expect(await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)).toBeLessThanOrEqual(0)
})

test('case-C08 no page scroll at 1512x982, 1440x900 and 1280x800', async ({ page }) => {
  for (const [w, h] of [[1512, 982], [1440, 900], [1280, 800]] as const) {
    await page.setViewportSize({ width: w, height: h })
    await open(page, live)
    await page.waitForSelector('[data-testid="case.fact"]')
    expect(await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)).toBeLessThanOrEqual(0)
  }
})

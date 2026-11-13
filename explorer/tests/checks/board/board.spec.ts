// board-C01..C07: the Board screen on the LIVE bundle, on a made-up RICH bundle (not routed), on the same bundle
// marked routed, and on an EMPTY one. Headless; 127.0.0.1 only. Apps: live 8860, rich 8861, routed 8862, empty 8863.
// Every expected value is read from the bundle on disk; none is written here.
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import type { BoardFiles, PartNotes, PartPlacements } from '../../../src/contract/records'
import { EXPLORER_ROOT, bundleEnv, byTestId, emptyBundle, startApp, watchConsole, type RunningApp } from '../../support'
import { makeRichBundle } from '../electronics/rich-bundle'

const LIVE = join(EXPLORER_ROOT, 'public', 'data')
const tmp = mkdtempSync(join(tmpdir(), 'bd-checks-'))
const RICH = makeRichBundle(join(tmp, 'rich'))
const ROUTED = makeRichBundle(join(tmp, 'routed'), { routed: true })
const read = <T>(dir: string, f: string): T => JSON.parse(readFileSync(join(dir, f), 'utf8')) as T

const apps: Record<string, RunningApp> = {}
test.beforeAll(async () => {
  apps.live = await startApp({ port: 8860, env: bundleEnv(LIVE) })
  apps.rich = await startApp({ port: 8861, env: bundleEnv(RICH) })
  apps.routed = await startApp({ port: 8862, env: bundleEnv(ROUTED) })
  apps.empty = await startApp({ port: 8863, env: bundleEnv(emptyBundle()) })
})
test.afterAll(async () => {
  for (const a of Object.values(apps)) await a?.stop()
  rmSync(tmp, { recursive: true, force: true })
})

const open = async (page: Page, app: RunningApp, search = '') => {
  await page.goto(`${app.url}/board${search}`)
  await page.waitForSelector('[data-testid="board.panel"]', { timeout: 100_000 })
}
const BUNDLES = [['live', LIVE], ['rich', RICH]] as const
const noise = (errs: string[]) => errs.filter((e) => !/Failed to load resource.*404/.test(e) && !/http 404: .*\/data\//.test(e))
/** the part id the card must show for a placement: its own, else the note that names the model object */
const expectedId = (p: BoardFiles['placements'][number], notes: PartNotes['notes']): string | null =>
  p.part_id ?? Object.entries(notes).find(([id, n]) => id.startsWith('ring:') && n.model_names.includes(p.name))?.[0] ?? null

for (const [name, dir] of BUNDLES) {
  const board = read<BoardFiles>(dir, 'board/index.json')
  const notes = read<PartNotes>(dir, 'content/part-notes.json').notes

  test(`board-C01 [${name}] not routed: the banner says so and names every missing item from the bundle`, async ({ page }) => {
    await open(page, apps[name]!)
    const banner = byTestId(page, 'app', 'panel').getByTestId('board.state-banner')
    await expect(banner).toContainText('not routed')
    for (const m of board.missing) await expect(banner).toContainText(m)
  })

  test(`board-C02 [${name}] one plan element per placement; Bottom hides every top part; a part opens its card`, async ({ page }) => {
    await open(page, apps[name]!)
    await expect(byTestId(page, 'board', 'plan-mark')).toHaveCount(board.placements.length)
    for (const p of board.placements.slice(0, 5)) await expect(page.locator(`[data-testid="board.plan-mark"][data-part="${p.name}"]`)).toHaveAttribute('data-side', p.side)
    await byTestId(page, 'board', 'side-bottom').click()
    await expect(byTestId(page, 'board', 'side-bottom')).toHaveAttribute('aria-pressed', 'true')
    await expect.poll(() => page.evaluate(() => [...document.querySelectorAll('[data-testid="board.plan-mark"][data-side="top"]')].filter((e) => getComputedStyle(e).visibility !== 'hidden').length), { timeout: 15_000 }).toBe(0)
    await byTestId(page, 'board', 'side-both').click()
    const p = board.placements[0]!
    await page.locator(`[data-testid="board.plan-mark"][data-part="${p.name}"]`).click()
    const id = expectedId(p, notes)
    if (id) await expect(page.locator(`[data-testid="board.part-card"][data-part-id="${id}"]`)).toBeVisible()
    else await expect(byTestId(page, 'board', 'part-card-no-line')).toContainText('no parts-list line')
  })

  test(`board-C03 [${name}] the stage shows the circuit board layer alone`, async ({ page }) => {
    const placements = read<PartPlacements>(dir, 'placements.json')
    const count = new Map<string, number>()
    for (const p of board.placements) {
      const id = expectedId(p, notes)
      const names = [p.name, ...(id ? notes[id]?.model_names ?? [] : [])]
      const l = placements.placements.find((x) => names.includes(x.name))?.layer
      if (l) count.set(l, (count.get(l) ?? 0) + 1)
    }
    const want = [...count.entries()].sort((a, b) => b[1] - a[1])[0]![0]
    await open(page, apps[name]!)
    await expect.poll(() => page.evaluate(() => window.__stage?.isolatedLayer?.() ?? null), { timeout: 60_000 }).toBe(want)
  })

  test(`board-C05 [${name}] no page scroll at 1512x982, 1440x900 and 1280x800`, async ({ page }) => {
    for (const [w, h] of [[1512, 982], [1440, 900], [1280, 800]] as const) {
      await page.setViewportSize({ width: w, height: h })
      await open(page, apps[name]!)
      expect(await page.evaluate(() => document.scrollingElement!.scrollHeight <= innerHeight)).toBe(true)
      expect(await page.evaluate(() => { const b = document.querySelector('[data-testid="app.panel-body"]')!; return b.scrollWidth <= b.clientWidth + 1 })).toBe(true)
    }
  })

  test(`board-C06 [${name}] a chosen part and side stay in the address and survive a reload`, async ({ page }) => {
    await open(page, apps[name]!)
    const p = board.placements[0]!
    await byTestId(page, 'board', 'side-top').click()
    await page.locator(`[data-testid="board.plan-mark"][data-part="${p.name}"]`).click({ force: true })
    await page.reload()
    await page.waitForSelector('[data-testid="board.plan-mark"]', { timeout: 100_000 })
    await expect(byTestId(page, 'board', 'side-top')).toHaveAttribute('aria-pressed', 'true', { timeout: 20_000 })
    await expect(page.locator(`[data-testid="board.plan-mark"][data-part="${p.name}"]`)).toHaveAttribute('aria-pressed', 'true', { timeout: 20_000 })
  })
}

test('board-C08 [live] the board file picture opens by default, at least 900 px wide at 1440x900; Top and Bottom switch it; a part row jumps to the part', async ({ page }) => {
  const board = read<BoardFiles>(LIVE, 'board/index.json')
  await page.setViewportSize({ width: 1440, height: 900 })
  await open(page, apps.live!, '?view=file')
  await expect.poll(async () => (await byTestId(page, 'board', 'svg-viewer').boundingBox())!.width, { timeout: 20_000 }).toBeGreaterThanOrEqual(900)
  const img = byTestId(page, 'board', 'svg-viewer-image')
  if (board.svg.top) await expect(img).toHaveAttribute('src', new RegExp(`${board.svg.top.replace(/[/.]/g, '\\$&')}$`))
  if (board.svg.bottom) {
    await byTestId(page, 'board', 'side-bottom').click()
    await expect(img).toHaveAttribute('src', new RegExp(`${board.svg.bottom.replace(/[/.]/g, '\\$&')}$`))
    await byTestId(page, 'board', 'side-top').click()
  }
  await byTestId(page, 'board', 'find').fill(board.placements[0]!.name)
  await page.locator(`[data-testid="board.placed-row"][data-part="${board.placements[0]!.name}"]`).click()
  await expect(byTestId(page, 'board', 'svg-viewer-focus')).toBeVisible({ timeout: 10_000 })
})

test('board-C04 routed: no "not routed" banner', async ({ page }) => {
  await open(page, apps.routed!)
  await expect(byTestId(page, 'board', 'plan-mark').first()).toBeVisible()
  await expect(byTestId(page, 'app', 'panel').getByTestId('board.state-banner')).toHaveCount(0)
})

test('board-C07 empty bundle: one banner with the command in <code>, no plan, 0 console errors', async ({ page }) => {
  const w = watchConsole(page)
  await open(page, apps.empty!)
  const banner = byTestId(page, 'app', 'panel').getByTestId('board.state-banner')
  await expect(banner).toHaveCount(1)
  await expect(banner.locator('code')).toHaveText('npm run collect')
  await expect(byTestId(page, 'board', 'plan-mark')).toHaveCount(0)
  expect(noise(w.errors)).toEqual([])
})

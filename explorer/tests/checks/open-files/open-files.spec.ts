// open-files-C01..C12: the Open items and files screen, on made-up bundles, the LIVE bundle and an EMPTY one.
// Headless; 127.0.0.1 only. The file starts its own apps (8821..8824) and stops only what it started.
import { createHash } from 'node:crypto'
import { readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import { EXPLORER_ROOT, bundleEnv, byTestId, emptyBundle, startApp, watchConsole, type RunningApp } from '../../support'
import { makeBundle } from './made'

const sha = (b: Buffer) => createHash('sha256').update(b).digest('hex')
const made = makeBundle('made')
const bare = makeBundle('bare')
const LIVE = join(EXPLORER_ROOT, 'public', 'data')
// read inside C12 only: the collector rewrites public/data while it runs, and that must not stop the other checks
const liveOf = () => ({
  open: JSON.parse(readFileSync(join(LIVE, 'open.json'), 'utf8')) as { supplier_requests: unknown[]; bench_tests: unknown[]; risks: unknown[]; decisions: unknown[] },
  files: JSON.parse(readFileSync(join(LIVE, 'files.json'), 'utf8')) as { files: { area: string }[] },
})

let a: RunningApp, b: RunningApp, c: RunningApp, d: RunningApp
test.beforeAll(async () => {
  a = await startApp({ port: 8821, env: bundleEnv(made.data, made.source) })
  b = await startApp({ port: 8822, env: bundleEnv(bare.data, bare.source) })
  c = await startApp({ port: 8823, env: bundleEnv(emptyBundle()) })
  d = await startApp({ port: 8824, env: bundleEnv(LIVE) })
})
test.afterAll(async () => {
  for (const x of [a, b, c, d]) await x?.stop()
})

const go = async (page: Page, app: RunningApp, path = '/open') => {
  await page.goto(app.url + path)
  await page.waitForSelector('[data-testid="open.panel"]')
}
const rows = (p: Page) => byTestId(p, 'open', 'item-row')

test('open-files-C01 four groups; 7 supplier rows each with who; decisions newest first', async ({ page }) => {
  const w = watchConsole(page)
  await go(page, a)
  await expect(byTestId(page, 'open', 'group-heading')).toHaveCount(4)
  await expect(rows(page)).toHaveCount(7 + 2 + 1 + 4)
  const sup = rows(page).and(page.locator('[data-group="supplier"]'))
  await expect(sup).toHaveCount(7)
  for (let i = 0; i < 7; i++) await expect(sup.nth(i).locator('[data-field="who"]')).toHaveText(/\S/)
  const dates = await rows(page).and(page.locator('[data-group="decision"]')).evaluateAll((els) => els.map((e) => e.getAttribute('data-date')))
  expect(dates).toEqual(['2026-05-09', '2026-05-02', '2026-03-15', '2026-02-01'])
  await expect(page.locator('[data-group="decision"] [data-testid="open.item-source"]').first()).toContainText('zz/notes.md')
  expect(w.errors).toEqual([])
})

test('open-files-C02 chip "waiting on a supplier": exactly the 7 supplier rows, aria-pressed, who chips narrow it', async ({ page }) => {
  await go(page, a)
  const chip = byTestId(page, 'open', 'filter-chip').filter({ hasText: 'waiting on a supplier' })
  const all = byTestId(page, 'open', 'filter-chip').filter({ hasText: /^all/ })
  await expect(all).toHaveAttribute('aria-pressed', 'true')
  await expect(chip).toHaveAttribute('aria-pressed', 'false')
  await chip.click()
  await expect(chip).toHaveAttribute('aria-pressed', 'true')
  await expect(all).toHaveAttribute('aria-pressed', 'false')
  await expect(rows(page)).toHaveCount(7)
  await expect(rows(page).and(page.locator('[data-group="supplier"]'))).toHaveCount(7)
  await byTestId(page, 'open', 'who-chip').filter({ hasText: 'zz-supplier-1' }).click()
  await expect(rows(page)).toHaveCount(2)
  for (const t of await byTestId(page, 'open', 'item-who').allTextContents()) expect(t).toBe('zz-supplier-1')
  await all.click()
  await expect(rows(page)).toHaveCount(14)
})

test('open-files-C03 a bundle with 0 supplier requests says "nothing waiting"', async ({ page }) => {
  await go(page, b)
  await expect(rows(page)).toHaveCount(7)
  await byTestId(page, 'open', 'filter-chip').filter({ hasText: 'waiting on a supplier' }).click()
  await expect(rows(page)).toHaveCount(0)
  await expect(byTestId(page, 'open', 'nothing')).toHaveText('nothing waiting')
})

test('open-files-C04 files: one group per area, rows with size and date, "+" file arrives with the disk bytes', async ({ page }) => {
  const w = watchConsole(page)
  await go(page, a, '/open#files')
  const areas = [...new Set(made.files.map((f) => f.area))]
  const groups = byTestId(page, 'open', 'file-group')
  await expect(groups).toHaveCount(areas.length)
  for (const area of areas) {
    const g = groups.and(page.locator(`[data-area="${area}"]`))
    await expect(g.locator('[data-testid="open.file-row"]')).toHaveCount(made.files.filter((f) => f.area === area).length)
  }
  const first = byTestId(page, 'open', 'file-row').first()
  await expect(first.locator('[data-testid="open.file-size"]')).toHaveText(/^\d+(\.\d)? (B|KB|MB)$/)
  await expect(first.locator('[data-testid="open.file-date"]')).toHaveText(/^\d{1,2} [A-Z][a-z]{2} 2026$/)
  const plus = made.files.find((f) => f.path.includes('+'))!
  await groups.and(page.locator(`[data-area="${plus.area}"]`)).locator('.disc-head').click()
  const row = page.locator(`[data-testid="open.file-row"][data-path="${plus.path}"]`)
  await expect(row.locator('[data-testid="open.file-open"]')).toHaveAttribute('target', '_blank')
  const [dl] = await Promise.all([page.waitForEvent('download'), row.locator('[data-testid="open.file-download"]').click()])
  expect(sha(readFileSync((await dl.path())!))).toBe(sha(made.disk.get(plus.path)!))
  expect(w.errors).toEqual([])
})

test('open-files-C05 "Download partner bundle": a zip of the bundle size; the page lists every entry', async ({ page }) => {
  const w = watchConsole(page)
  await go(page, a, '/open#files')
  const btn = byTestId(page, 'open', 'download-bundle')
  await expect(btn).toBeEnabled()
  const [dl] = await Promise.all([page.waitForEvent('download'), btn.click()])
  expect(dl.suggestedFilename()).toMatch(/\.zip$/)
  const bytes = readFileSync((await dl.path())!)
  expect(bytes.length).toBe(made.bundle!.size_bytes)
  expect(statSync(join(made.data, 'bundle.zip')).size).toBe(bytes.length)
  await expect(byTestId(page, 'open', 'bundle-entry')).toHaveCount(made.bundle!.contents.length)
  expect(w.errors).toEqual([])
})

test('open-files-C06 hand-off sets are read from the files list: manufacturer kinds, printer parts and ring sizes', async ({ page }) => {
  await go(page, a, '/open#files')
  const mfg = page.locator('[data-testid="open.file-set"][data-set="manufacturer"]')
  const printer = page.locator('[data-testid="open.file-set"][data-set="printer"]')
  await expect(mfg.locator('[data-testid="open.set-row"]')).toHaveCount(5)
  for (const k of ['wiring', 'parts-list', 'spec', 'drawing', 'step']) await expect(mfg.locator(`[data-kind-id="${k}"]`)).toHaveCount(1)
  await expect(printer.locator('[data-testid="open.set-row"]')).toHaveCount(10)
  await expect(printer.locator('[data-part]')).toHaveCount(2)
  const body = printer.locator('[data-part="body"]')
  expect(await body.locator('.fl-base').allTextContents()).toEqual([5, 6, 7, 8, 9, 10, 11, 12, 13].map((n) => `Ring size ${n}`))
  const row = printer.locator('[data-testid="open.set-row"]').first()
  const [dl] = await Promise.all([page.waitForEvent('download'), row.locator('[data-testid="open.file-download"]').click()])
  const path = (await row.getAttribute('data-path'))!
  expect(sha(readFileSync((await dl.path())!))).toBe(sha(made.disk.get(path)!))
})

test('open-files-C07 empty hand-off folder: "Not made yet" with what is coming, no dead link', async ({ page }) => {
  await go(page, b, '/open#files')
  for (const set of ['printer', 'manufacturer']) {
    const s = page.locator(`[data-testid="open.file-set"][data-set="${set}"]`)
    await expect(s.locator('[data-testid="open.file-set-empty"]')).toContainText('Not made yet')
    await expect(s.locator('a')).toHaveCount(0)
  }
})

test('open-files-C08 no zip in the bundle: the button is disabled and says "run npm run collect"', async ({ page }) => {
  const w = watchConsole(page)
  await go(page, b, '/open#files')
  const btn = byTestId(page, 'open', 'download-bundle')
  await expect(btn).toBeDisabled()
  await expect(btn).toContainText('run npm run collect')
  await expect(byTestId(page, 'open', 'bundle-entry')).toHaveCount(0)
  expect(w.errors).toEqual([])
})

test('open-files-C09 empty bundle: honest banners with the command, title and a disabled button, 0 console errors', async ({ page }) => {
  const w = watchConsole(page)
  await go(page, c, '/open#files')
  // the stage draws its own banner with the same id: count the panel's only
  const banners = byTestId(page, 'app', 'panel').getByTestId('open.state-banner')
  await expect(banners).toHaveCount(2)
  for (let i = 0; i < 2; i++) await expect(banners.nth(i).locator('code')).toHaveText('npm run collect')
  await expect(page.getByRole('heading', { name: 'Open items and files' })).toBeVisible()
  await expect(byTestId(page, 'open', 'download-bundle')).toBeDisabled()
  await expect(rows(page)).toHaveCount(0)
  expect(w.errors.filter((e) => !/Failed to load resource.*404|http 404: .*\/data\//.test(e)), 'only the absent-bundle 404 of /data/ is allowed').toEqual([])
})

test('open-files-C10 the top bar "Files" lands on the files section; "Open items" returns to the top', async ({ page }) => {
  await page.goto(a.url + '/')
  await page.getByTestId('app.tab-open').click()
  await page.waitForSelector('[data-testid="open.panel"]')
  await page.getByTestId('app.tab-files').click()
  await expect.poll(() => new URL(page.url()).hash).toBe('#files')
  const top = () => page.evaluate(() => document.getElementById('files')!.getBoundingClientRect().top - document.querySelector('.panel-body')!.getBoundingClientRect().top)
  await expect.poll(top, { timeout: 5000 }).toBeLessThan(60)
  await page.getByTestId('app.tab-open').click()
  await expect.poll(() => page.evaluate(() => document.querySelector('.panel-body')!.scrollTop), { timeout: 5000 }).toBe(0)
})

test('open-files-C11 no page scroll at 1512x982, 1440x900 and 1280x800; the panel does not overflow sideways', async ({ page }) => {
  for (const [w, h] of [[1512, 982], [1440, 900], [1280, 800]] as const) {
    await page.setViewportSize({ width: w, height: h })
    await go(page, a)
    expect(await page.evaluate(() => document.documentElement.scrollHeight <= window.innerHeight && document.documentElement.scrollWidth <= window.innerWidth), `${w}x${h}`).toBe(true)
    expect(await page.evaluate(() => { const p = document.querySelector('.panel-body')!; return p.scrollWidth <= p.clientWidth }), `panel overflows sideways at ${w}x${h}`).toBe(true)
  }
})

test('open-files-C12 live bundle: every open item and every file of the bundle is on screen', async ({ page }) => {
  const w = watchConsole(page)
  await go(page, d, '/open#files')
  const { open: live, files: liveFiles } = liveOf()
  await expect(rows(page)).toHaveCount(live.supplier_requests.length + live.bench_tests.length + live.risks.length + live.decisions.length)
  await expect(byTestId(page, 'open', 'file-group')).toHaveCount(new Set(liveFiles.files.map((f) => f.area)).size)
  await expect(byTestId(page, 'open', 'file-row')).toHaveCount(liveFiles.files.length)
  expect(w.errors).toEqual([])
})

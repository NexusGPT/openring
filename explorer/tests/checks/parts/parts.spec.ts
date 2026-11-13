// parts-C01..C09: the Parts screen, on the LIVE bundle, the SAMPLE bundle (made-up values) and an EMPTY one.
// Headless; 127.0.0.1 only. One app at a time on 8806. Values are read from the bundle on disk; none is written here.
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import type { Manifest, Parts, SchematicPages } from '../../../src/contract/records'
import { EXPLORER_ROOT, SAMPLE_BUNDLE, bundleEnv, byTestId, emptyBundle, portInUse, startApp, watchConsole, type RunningApp } from '../../support'

const PORT = 8806
const LIVE = join(EXPLORER_ROOT, 'public', 'data')
const read = <T>(dir: string, f: string): T => JSON.parse(readFileSync(join(dir, f), 'utf8')) as T
const parts = read<Parts>(LIVE, 'parts.json')
const manifest = read<Manifest>(LIVE, 'manifest.json')
const ring = parts.lines.filter((l) => l.bom === 'ring')
const withAction = ring.filter((l) => (l.open_action ?? '').trim() !== '')
const withCode = ring.filter((l) => (l.maker_part_number ?? '').trim() !== '')
const sha = (b: Buffer) => createHash('sha256').update(b).digest('hex')

let app: RunningApp
const serve = async (bundle: string, source?: string) => {
  // the previous app is stopped by group; wait until its port is really free
  for (let i = 0; i < 50 && (await portInUse(PORT)); i++) await new Promise((r) => setTimeout(r, 200))
  app = await startApp({ port: PORT, env: bundleEnv(bundle, source) })
}
const open = async (page: Page, query = '') => {
  await page.goto(`${app.url}/parts${query}`)
  await page.waitForSelector('[data-testid="parts.panel"]')
}
const rows = (page: Page) => byTestId(page, 'parts', 'row')
const noise = (e: string) => /http 404: .*\/data\//.test(e) || /Failed to load resource.*404/.test(e) || /WebGL|GPU stall|swiftshader/i.test(e)

test.describe('live bundle', () => {
  test.beforeAll(() => serve(LIVE))
  test.afterAll(() => app?.stop())

  test('parts-C01 one row per ring line; every cell equals the bundle; totals read the bundle totals', async ({ page }) => {
    const w = watchConsole(page)
    await open(page)
    await expect(rows(page)).toHaveCount(parts.totals.ring.lines)
    const totals = byTestId(page, 'parts', 'totals')
    await expect(totals).toContainText(`${parts.totals.ring.lines} lines`)
    await expect(totals).toContainText(`${parts.totals.ring.parts} parts`)
    for (const l of ring) {
      const row = page.locator(`[data-testid="parts.row"][data-part-id="${l.part_ids[0]}"]`)
      await expect(row, l.part_ids[0]).toContainText(l.item)
      if (l.maker_part_number) await expect(row.getByTestId('parts.order-code')).toHaveText(l.maker_part_number)
      else await expect(row.getByTestId('parts.order-code')).toHaveText('made to drawing')
      if (l.price) await expect(row).toContainText(l.price.raw)
      if (l.open_action) await expect(row.getByTestId('parts.open-action')).toContainText(l.open_action.slice(0, 40))
    }
    expect(w.errors.filter((e) => !noise(e))).toEqual([])
  })

  test('parts-C02 a click on a row opens that line card in place; Escape and a second click close it; the address holds the part', async ({ page }) => {
    await open(page)
    const l = ring[Math.min(4, ring.length - 1)]!
    const id = l.part_ids[0]!
    const row = page.locator(`[data-testid="parts.row"][data-part-id="${id}"]`)
    await row.click()
    const card = byTestId(page, 'parts', 'part-card')
    await expect(card).toHaveCount(1)
    await expect(card).toHaveAttribute('data-part-id', id)
    await expect(row).toHaveAttribute('aria-expanded', 'true')
    expect(new URL(page.url()).searchParams.get('part')).toBe(id)
    await page.keyboard.press('Escape')
    await expect(card).toHaveCount(0)
    expect(new URL(page.url()).searchParams.get('part')).toBeNull()
    await row.click()
    await row.click()
    await expect(card).toHaveCount(0)
    // an address with ?part= opens the card on load
    await open(page, `?part=${encodeURIComponent(id)}`)
    await expect(byTestId(page, 'parts', 'part-card')).toHaveAttribute('data-part-id', id)
  })

  test('parts-C03 needs-a-supplier leaves only lines with an open action; reload keeps it; clear all restores every line', async ({ page }) => {
    await open(page)
    const chip = page.locator('[data-testid="parts.filter-chip"][data-filter="supplier"]')
    await chip.click()
    await expect(rows(page)).toHaveCount(withAction.length)
    await expect(chip).toHaveAttribute('aria-pressed', 'true')
    for (const r of await rows(page).all()) await expect(r.getByTestId('parts.open-action')).not.toBeEmpty()
    expect(new URL(page.url()).searchParams.get('f')).toBe('supplier')
    await page.reload()
    await page.waitForSelector('[data-testid="parts.panel"]')
    await expect(rows(page)).toHaveCount(withAction.length)
    await byTestId(page, 'parts', 'filter-clear').click()
    await expect(rows(page)).toHaveCount(ring.length)
    expect(new URL(page.url()).searchParams.get('f')).toBeNull()
    await expect(byTestId(page, 'parts', 'filter-clear')).toHaveCount(0)
  })

  test('parts-C04 has-code and made-to-drawing split the list; they never hold together; they combine with supplier', async ({ page }) => {
    await open(page)
    const chip = (f: string) => page.locator(`[data-testid="parts.filter-chip"][data-filter="${f}"]`)
    await chip('code').click()
    await expect(rows(page)).toHaveCount(withCode.length)
    await chip('drawing').click()
    await expect(rows(page)).toHaveCount(ring.length - withCode.length)
    await expect(chip('code')).toHaveAttribute('aria-pressed', 'false')
    await chip('supplier').click()
    await expect(rows(page)).toHaveCount(withAction.filter((l) => !(l.maker_part_number ?? '').trim()).length)
    await expect(byTestId(page, 'parts', 'shown')).toContainText(`of ${ring.length} lines`)
  })

  test('parts-C05 Export CSV downloads bom.csv byte for byte, whatever the filter', async ({ page }) => {
    await open(page, '?f=supplier')
    const source = ring[0]!.source.file
    const [dl] = await Promise.all([page.waitForEvent('download'), byTestId(page, 'parts', 'export-csv').click()])
    expect(dl.suggestedFilename()).toBe('bom.csv')
    const path = await dl.path()
    expect(sha(readFileSync(path))).toBe(sha(readFileSync(join(EXPLORER_ROOT, '..', source))))
  })

  test('parts-C06 the charging case sits in its own group, off the ring totals, dimmed with the contract sentence', async ({ page }) => {
    await open(page)
    await expect(byTestId(page, 'parts', 'case-row')).toHaveCount(0)
    await byTestId(page, 'parts', 'case-toggle').click()
    await expect(byTestId(page, 'parts', 'case-row')).toHaveCount(parts.totals.case.lines)
    await expect(rows(page)).toHaveCount(parts.totals.ring.lines)
    const m = /case lines were made for design (\S+?); the design is now (\S+?)\./i.exec(manifest.records.parts.message ?? '')
    const banner = byTestId(page, 'parts', 'section-case').getByTestId('parts.state-banner')
    if (m) {
      await expect(banner).toContainText(`Made for design ${m[1]}; the design is now ${m[2]}.`)
      await expect(page.locator('.pt-case')).toHaveAttribute('data-dimmed', 'true')
    } else await expect(banner).toHaveCount(0)
  })

  test('parts-C07 no page scroll at 1512x982, 1440x900 and 1280x800; rows are at least 40 px tall, names at most 4 lines', async ({ page }) => {
    for (const [w, h] of [[1512, 982], [1440, 900], [1280, 800]] as const) {
      await page.setViewportSize({ width: w, height: h })
      await open(page)
      expect(await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)).toBeLessThanOrEqual(0)
      const box = (await rows(page).first().boundingBox())!
      expect(box.height).toBeGreaterThanOrEqual(40)
      // a long refs list never squeezes a line's name into a thin column: no name is taller than 4 lines (80 px)
      for (const n of await page.locator('.pt-name').all()) expect((await n.boundingBox())!.height, await n.innerText()).toBeLessThanOrEqual(80)
    }
  })

  test('parts-C08 the selected line is the address the stage reads, and it survives a filter change', async ({ page }) => {
    await open(page)
    const id = ring[0]!.part_ids[0]!
    await page.locator(`[data-testid="parts.row"][data-part-id="${id}"]`).click()
    await expect(byTestId(page, 'parts', 'part-card')).toHaveCount(1)
    await page.locator('[data-testid="parts.filter-chip"][data-filter="supplier"]').click()
    const q = new URL(page.url()).searchParams
    expect(q.get('part')).toBe(id)
    expect(q.get('f')).toBe('supplier')
  })
})

test.describe('sample bundle (made-up values)', () => {
  test.beforeAll(() => serve(SAMPLE_BUNDLE, join(EXPLORER_ROOT, 'tests', 'support', 'sample-source')))
  test.afterAll(() => app?.stop())
  const sp = read<Parts>(SAMPLE_BUNDLE, 'parts.json')
  const sring = sp.lines.filter((l) => l.bom === 'ring')
  const pages = read<SchematicPages>(SAMPLE_BUNDLE, 'schematic/index.json')

  test('parts-C09 sample: rows, a grouped line switches its card by reference, the page filter keeps that page only', async ({ page }) => {
    await open(page)
    await expect(rows(page)).toHaveCount(sring.length)
    await expect(byTestId(page, 'parts', 'totals')).toContainText(`${sp.totals.ring.parts} parts`)
    const grouped = sring.find((l) => l.part_ids.length > 1)!
    await page.locator(`[data-testid="parts.row"][data-part-id="${grouped.part_ids[0]}"]`).click()
    const chips = byTestId(page, 'parts', 'ref-chip')
    await expect(chips).toHaveCount(grouped.part_ids.length)
    await chips.nth(1).click()
    await expect(byTestId(page, 'parts', 'part-card')).toHaveAttribute('data-part-id', grouped.part_ids[1]!)
    const pg = pages.pages[0]!
    await open(page, `?page=${pg.id}`)
    const onPage = sring.filter((l) => l.part_ids.some((id) => pg.part_ids.includes(id)))
    await expect(rows(page)).toHaveCount(onPage.length)
    await byTestId(page, 'parts', 'filter-clear').click()
    await expect(rows(page)).toHaveCount(sring.length)
  })
})

test.describe('empty bundle', () => {
  test.beforeAll(() => serve(emptyBundle()))
  test.afterAll(() => app?.stop())

  test('parts-C10 empty bundle: one honest banner with the command, no rows, a disabled export, 0 console errors', async ({ page }) => {
    const w = watchConsole(page)
    await open(page)
    const banner = byTestId(page, 'app', 'panel').getByTestId('parts.state-banner')
    await expect(banner).toHaveCount(1)
    await expect(banner.locator('code')).toHaveText('npm run collect')
    await expect(rows(page)).toHaveCount(0)
    await expect(byTestId(page, 'parts', 'totals')).toHaveCount(0)
    expect(w.errors.filter((e) => !noise(e))).toEqual([])
  })
})

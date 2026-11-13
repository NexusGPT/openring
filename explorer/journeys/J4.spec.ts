// J4: Follow the circuit from a block to a part (docs/JOURNEYS.md J4.1 to J4.3; rows J4#1 to J4#3 of docs/TEST-PLAN.md section 3).
// Written from the journey table. Every expected value is read from the bundle (electronics.json, schematic/index.json,
// parts.json, content/part-notes.json); none is typed here. The journey says "4 microphones, U5, 8 pages" of an earlier
// design: here the block is the one whose label is Microphones, the part is the first part of that page, the pages are the record's.
// Ids on the page: home.area-tile; electronics.diagram, .block (data-block), .page-pane, .svg-viewer (data-scale, data-picture),
// .svg-viewer-fit, .page-tab (data-page), .parts-list, .part-row (data-part), .part-card (data-part-id), .tab-pins, .tab-power,
// .pin-row, .power-row, .parts-of-page; parts.row (data-part-id, aria-expanded), parts.filter-chip (data-filter), parts.shown, parts.card-slot.
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect as baseExpect, test, type Locator, type Page } from '@playwright/test'
import { FIXTURE_DATA, blockOffline, byTestId, watchConsole } from '../tests/support'

const expect = baseExpect.configure({ timeout: 20_000 })
test.describe.configure({ timeout: 90_000 })
test.use({ viewport: { width: 1440, height: 900 } })

const J4_1 = "J4#1"
const J4_2 = "J4#2"
const J4_3 = "J4#3"

const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
function bundleRecord<T>(file: string): T {
  if (!existsSync(join(BUNDLE, 'manifest.json'))) throw new Error(`journey setup: no bundle at ${BUNDLE}; set EXPLORER_BUNDLE`)
  const p = join(BUNDLE, file)
  if (!existsSync(p)) throw new Error(`journey setup: record ${file} is missing from the bundle ${BUNDLE}`)
  return JSON.parse(readFileSync(p, 'utf8')) as T
}
interface Block { id: string; label: string; sheet?: string }
interface Elec { blocks: Block[]; pin_plan: { rows: unknown[] | number }; power_budget: { rows: unknown[] | number } }
interface Pages { pages: { id: string; part_ids: string[] }[] }
interface Line { part_ids: string[]; open_action: string | null; item: string }
const elec = () => bundleRecord<Elec>('electronics.json')
const pages = () => bundleRecord<Pages>('schematic/index.json').pages
const lines = () => bundleRecord<{ lines: Line[] }>('parts.json').lines
const rowCount = (t: { rows: unknown[] | number }) => (Array.isArray(t.rows) ? t.rows.length : t.rows)
/** The block of the journey (Microphones), its page, and the part the journey zooms into (the first part of that page). */
function subject() {
  const block = elec().blocks.find((b) => /microphone/i.test(b.label))
  if (!block) throw new Error('journey setup: no block labelled Microphones in electronics.json')
  const page = pages().find((p) => p.id === (block.sheet ?? block.id))
  if (!page || page.part_ids.length === 0) throw new Error(`journey setup: no page with parts for block '${block.id}'`)
  return { block, page, part: page.part_ids.find((p) => p.endsWith(':U5')) ?? page.part_ids[0]! }
}

async function openElectronics(page: Page): Promise<void> {
  const w = watchConsole(page)
  await blockOffline(page, w)
  await page.goto('/')
  const tile = byTestId(page, 'home', 'area-tile').and(page.locator('[data-area="electronics"]'))
  await expect(tile, 'Home has no Electronics tile').toBeVisible()
  await tile.click()
  await expect(page, 'the Electronics tile did not go to /electronics').toHaveURL(/\/electronics(\/|\?|#|$)/)
  await expect(byTestId(page, 'electronics', 'diagram'), 'Electronics has no block diagram (electronics.diagram)').toBeVisible()
}
const block = (page: Page, id: string): Locator => byTestId(page, 'electronics', 'block').and(page.locator(`[data-block="${id}"]`))
async function chooseBlock(page: Page, id: string): Promise<void> {
  await expect(block(page, id), `no block '${id}' (electronics.block[data-block])`).toBeVisible()
  await block(page, id).click()
  await expect(byTestId(page, 'electronics', 'page-pane'), 'no wiring page opened (electronics.page-pane)').toBeVisible()
  await expect(byTestId(page, 'electronics', 'svg-viewer')).toHaveAttribute('data-picture', 'ready')
}
const viewer = (page: Page) => byTestId(page, 'electronics', 'svg-viewer')
const scale = async (page: Page) => Number(await viewer(page).getAttribute('data-scale'))

// ---- J4.1 --------------------------------------------------------------------------------------------
test(`${J4_1} (J4.1) Electronics: the block diagram lists the blocks; "Microphones" opens its page large`, async ({ page }) => {
  await openElectronics(page)
  const e = elec()
  const blocks = byTestId(page, 'electronics', 'block')
  await expect(blocks).toHaveCount(e.blocks.length)
  for (const b of e.blocks) await expect(block(page, b.id), `block '${b.id}' does not show its label`).toContainText(b.label)
  const s = subject()
  await chooseBlock(page, s.block.id)
  await expect(block(page, s.block.id)).toHaveAttribute('aria-pressed', 'true')
  const box = (await viewer(page).boundingBox())!
  expect(box.width, `the wiring picture is ${Math.round(box.width)} px wide at 1440 x 900; it must be at least 900`).toBeGreaterThanOrEqual(900)
  const img = byTestId(page, 'electronics', 'svg-viewer-image')
  await expect.poll(() => img.evaluate((el) => (el instanceof HTMLImageElement ? el.naturalWidth : 0)), { message: 'the wiring picture did not load (naturalWidth stays 0)' }).toBeGreaterThan(0)
})

// ---- J4.2 --------------------------------------------------------------------------------------------
test(`${J4_2} (J4.2) Electronics: page list, parts of the page, a part row zooms the picture and opens its card; pin plan and power budget`, async ({ page }) => {
  await openElectronics(page)
  const s = subject()
  await chooseBlock(page, s.block.id)

  // the page list holds every page of the record
  const tabs = byTestId(page, 'electronics', 'page-tab')
  await expect(tabs).toHaveCount(pages().length)
  for (const p of pages()) await expect(tabs.and(page.locator(`[data-page="${p.id}"]`)), `no tab for page '${p.id}'`).toHaveCount(1)

  // the parts of this page equal the record's
  const rows = byTestId(page, 'electronics', 'part-row')
  await expect(rows).toHaveCount(s.page.part_ids.length)
  const got = (await rows.evaluateAll((els) => els.map((e) => e.getAttribute('data-part') ?? ''))).sort()
  expect(got, 'the parts of the page differ from the record').toEqual([...s.page.part_ids].sort())

  // zoom into the part: the scale rises above the fitted one and the card opens
  await byTestId(page, 'electronics', 'svg-viewer-fit').click()
  await page.waitForTimeout(800)
  const fit = await scale(page)
  const row = rows.and(page.locator(`[data-part="${s.part}"]`))
  await expect(row).toHaveCount(1)
  await row.click()
  await expect.poll(() => scale(page), { message: `the picture did not zoom to ${s.part} (scale stayed at fit ${fit})` }).toBeGreaterThan(fit * 1.2)
  await expect(byTestId(page, 'electronics', 'part-card'), 'no part card opened for the part').toHaveAttribute('data-part-id', s.part)
  const notes = bundleRecord<{ notes: Record<string, { what: string }> }>('content/part-notes.json').notes
  if (notes[s.part]) await expect(byTestId(page, 'electronics', 'part-card')).toContainText(notes[s.part]!.what)

  // pin plan and power budget: the record's row counts
  await byTestId(page, 'electronics', 'tab-pins').click()
  await expect(byTestId(page, 'electronics', 'pin-row'), 'pin plan rows differ from the record').toHaveCount(rowCount(elec().pin_plan))
  await byTestId(page, 'electronics', 'tab-power').click()
  await expect(byTestId(page, 'electronics', 'power-row'), 'power budget rows differ from the record').toHaveCount(rowCount(elec().power_budget))
})

// ---- J4.3 --------------------------------------------------------------------------------------------
test(`${J4_3} (J4.3) Electronics to Parts: "parts of this page" filters the list; a chip shortens it; the part opens its card`, async ({ page }) => {
  await openElectronics(page)
  const s = subject()
  await chooseBlock(page, s.block.id)
  await byTestId(page, 'electronics', 'part-row').and(page.locator(`[data-part="${s.part}"]`)).click()
  await expect(byTestId(page, 'electronics', 'part-card')).toHaveAttribute('data-part-id', s.part)
  const link = byTestId(page, 'electronics', 'parts-of-page')
  await expect(link, 'no "parts of this page" link (electronics.parts-of-page)').toBeVisible()
  await link.click()
  await expect(page).toHaveURL(/\/parts(\/|\?|#|$)/)

  // the list holds the lines of that page
  const onPage = lines().filter((l) => l.part_ids.some((id) => s.page.part_ids.includes(id)))
  expect(onPage.length, 'control: no parts-list line for the page').toBeGreaterThan(0)
  const rows = byTestId(page, 'parts', 'row')
  await expect(rows, 'the Parts list is not filtered to the page').toHaveCount(onPage.length)

  // the part reached from Electronics is highlighted (its line is the open one)
  const mine = rows.and(page.locator(`[data-part-id="${s.part}"]`))
  await expect(mine, `the line of ${s.part} is not in the list`).toHaveCount(1)
  await expect(mine, `the part ${s.part} reached from Electronics is not highlighted (its row is not open)`).toHaveAttribute('aria-expanded', 'true')
  await expect(byTestId(page, 'parts', 'card-slot')).toBeVisible()

  // a filter chip shortens the list to the record's count: lines with something still to ask a supplier
  const chip = byTestId(page, 'parts', 'filter-chip').and(page.locator('[data-filter="supplier"]'))
  await expect(chip, 'no filter chip "supplier" (parts.filter-chip[data-filter=supplier])').toBeVisible()
  const want = onPage.filter((l) => !!l.open_action).length
  expect(want, 'control: the record has no line of the page with an open action').toBeGreaterThan(0)
  expect(want, 'control: the chip cannot shorten the list').toBeLessThan(onPage.length)
  await chip.click()
  await expect(rows, 'the chip did not shorten the list to the record count').toHaveCount(want)
})

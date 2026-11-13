// J7: See the charging case (docs/JOURNEYS.md J7.1 and J7.2; rows J7#1 and J7#2 of docs/TEST-PLAN.md section 3).
// Written from the signed journey table, never from a built screen. Every expected value (key numbers, lid node, pins,
// parts, supplier items, honest state) is read from the bundle at run time (EXPLORER_BUNDLE). Entry: Home, tile "Case".
// Headless only. Ids on the page: case.{panel,numbers,fact,lid-toggle,selected,selected-line,part-card,parts-list,part-row,
// parts-count,supplier-items,supplier-item,state-banner,stale-reason}; window.__stage.nodeRotationDeg(lid node).
// Red-first switches (never set in a normal run): J7_SKIP_CLICK=1 (no click on the lid button), J7_FACT_SUFFIX (a wrong
// expected fact), J7_PIN (the pin node clicked in J7.2).
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect as baseExpect, test, type Locator, type Page } from '@playwright/test'
import { FIXTURE_DATA, blockOffline, byTestId, watchConsole } from '../tests/support'

const expect = baseExpect.configure({ timeout: 8_000 })
test.describe.configure({ timeout: 90_000 })

const J7_1 = 'J7#1'
const J7_2 = 'J7#2'

const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
function bundleRecord<T>(file: string): T {
  if (!existsSync(join(BUNDLE, 'manifest.json'))) throw new Error(`journey setup: no bundle at ${BUNDLE} (manifest.json missing); set EXPLORER_BUNDLE`)
  const p = join(BUNDLE, file)
  if (!existsSync(p)) throw new Error(`journey setup: record ${file} is missing from the bundle ${BUNDLE}`)
  return JSON.parse(readFileSync(p, 'utf8')) as T
}

interface Fact { id: string; label: string; value: string | number; unit: string | null }
interface CaseRec {
  facts: Fact[]
  glb: { lid_node: string; nodes: { name: string; part_ids: string[] }[] } | null
  part_ids: string[]
  supplier_items: { id: string; item: string; who: string; ask: string }[]
}
interface PartsLine { bom: string; row: number; item: string; function: string | null; refs: string[]; quantity: number; part_ids: string[] }
interface Parts { lines: PartsLine[]; totals: { case: { lines: number; parts: number } } }
interface Manifest { records: Record<string, { status: string; basis_version: string | null; current_version: string | null; message: string | null }> }

// ---- page helpers ------------------------------------------------------------------------------------
const tile = (page: Page, area: string): Locator => byTestId(page, 'home', 'area-tile').and(page.locator(`[data-area="${area}"]`))
const lid = (page: Page) => byTestId(page, 'case', 'lid-toggle')
async function boot(page: Page) {
  const w = watchConsole(page)
  await blockOffline(page, w)
  return w
}
async function stageReady(page: Page): Promise<void> {
  await expect
    .poll(() => page.evaluate(() => window.__stage?.ready === true), { timeout: 20_000, message: 'the 3D stage never reported ready: window.__stage is missing or not ready' })
    .toBe(true)
}
async function toCase(page: Page): Promise<void> {
  await page.goto('/')
  const t = tile(page, 'case')
  await expect(t, 'Home has no Case tile (home.area-tile[data-area=case])').toBeVisible()
  await t.click()
  await expect(page, 'the tile "Case" did not go to /case').toHaveURL(/\/case(\/|\?|#|$)/)
  await expect(byTestId(page, 'case', 'panel'), 'no Case panel (case.panel)').toBeVisible()
  await stageReady(page)
}
/** The text of one fact as the record states it: the value, plus the unit when the value does not carry it. */
const factText = (f: Fact): string => {
  const v = String(f.value)
  return f.unit && !v.toLowerCase().includes(f.unit.toLowerCase()) ? `${v} ${f.unit}` : v
}
const lidDeg = (page: Page) => page.evaluate((n) => window.__stage!.nodeRotationDeg(n), caseRec().glb!.lid_node)
const caseRec = () => bundleRecord<CaseRec>('case/index.json')
/** The card's heading in plain words: the hand-written note's 'what' when the part has one, else the parts-list item. */
const headingOf = (id: string, l: PartsLine): string => {
  const notes = bundleRecord<{ notes: Record<string, { what?: string }> }>('content/part-notes.json').notes
  return notes[id]?.what ?? l.item
}
const nums = (s: string) => (s.match(/\d+(?:\.\d+)?/g) ?? []).map(Number)

test(`${J7_1} (J7.1) Case: the key numbers equal the case record; the honest state is right; "Open the lid" opens it and "Close the lid" shuts it`, async ({ page }) => {
  const w = await boot(page)
  const c = caseRec()
  const parts = bundleRecord<Parts>('parts.json')
  const manifest = bundleRecord<Manifest>('manifest.json')
  expect(c.glb, 'control: the case record has no 3D model (glb)').toBeTruthy()
  await toCase(page)

  // sees: the key numbers are exactly the record's facts (outer size, cell capacity, transfer time among them)
  const facts = byTestId(page, 'case', 'fact')
  await expect(facts, 'the key numbers list a different number of facts than the case record').toHaveCount(c.facts.length)
  for (const f of c.facts) {
    const row = facts.and(page.locator(`[data-fact="${f.id}"]`))
    await expect(row, `no key number for the fact '${f.id}'`).toHaveCount(1)
    await expect(row.locator('.cs-fact-label'), `the label of '${f.id}' differs from the record`).toHaveText(f.label)
    await expect(row.locator('.cs-fact-value'), `the value of '${f.label}' differs from the record (${factText(f)})`).toHaveText(factText(f) + (process.env.J7_FACT_SUFFIX ?? ''))
  }
  for (const id of ['case-size', 'case-cell', 'case-transfer']) expect(c.facts.some((f) => f.id === id), `control: the record has no fact '${id}'`).toBe(true)
  const size = c.facts.find((f) => f.id === 'case-size')!
  expect(nums(String(size.value)).length, 'control: the outer size does not read as three numbers').toBe(3)
  await expect(byTestId(page, 'case', 'numbers')).toContainText(String(size.value))

  // honest state: the stale sentence shows exactly when the record is stale (the record's own state, from the manifest)
  const entry = manifest.records['case']!
  const banner = byTestId(page, 'case', 'state-banner')
  if (entry.status === 'stale') {
    await expect(banner, 'the case record is stale but no banner says so').toContainText(`Made for design ${entry.basis_version}; the design is now ${entry.current_version}.`)
  } else {
    expect(entry.status, `the case record is '${entry.status}': this test expects ok or stale`).toBe('ok')
    await expect(banner, 'a state banner shows although the case record is ok').toHaveCount(0)
    await expect(byTestId(page, 'case', 'stale-reason'), 'a stale reason shows although the case record is ok').toHaveCount(0)
  }

  // does: opens the lid. The lid starts shut (angle 0), the button offers to open it, then it reaches an open angle and the label flips
  const open = lid(page)
  await expect(open, 'no lid button (case.lid-toggle)').toBeVisible()
  await expect(open).toHaveText('Open the lid')
  await expect(open).toHaveAttribute('data-open', 'false')
  expect(await lidDeg(page), 'the lid is not shut before the click').toBeCloseTo(0, 0)
  if (!process.env.J7_SKIP_CLICK) await open.click()
  await expect(open, 'the button label did not change to "Close the lid"').toHaveText('Close the lid')
  await expect(open).toHaveAttribute('data-open', 'true')
  await expect.poll(() => lidDeg(page), { timeout: 8_000, message: 'the lid did not open: nodeRotationDeg(lid) stayed below 90' }).toBeGreaterThanOrEqual(90)

  // and closes again
  await open.click()
  await expect(open, 'the button label did not return to "Open the lid"').toHaveText('Open the lid')
  await expect.poll(() => lidDeg(page), { timeout: 8_000, message: 'the lid did not close: nodeRotationDeg(lid) did not return to 0' }).toBeLessThan(1)

  // the supplier items listed equal the record's count and words; the case parts list equals the totals
  const asks = byTestId(page, 'case', 'supplier-item')
  expect(c.supplier_items.length, 'control: the record lists no supplier item').toBeGreaterThan(0)
  await expect(asks, 'the supplier items listed differ in number from the record').toHaveCount(c.supplier_items.length)
  for (const [i, s] of c.supplier_items.entries()) {
    await expect(asks.nth(i), `supplier item ${i} does not show the record's item text`).toContainText(s.item)
    await expect(asks.nth(i)).toContainText(s.who)
  }
  const caseLines = parts.lines.filter((l) => l.bom === 'case')
  expect(caseLines.length, 'control: the parts list has no case lines').toBe(parts.totals.case.lines)
  await expect(byTestId(page, 'case', 'parts-count')).toContainText(`${parts.totals.case.lines} lines`)
  await expect(byTestId(page, 'case', 'parts-count')).toContainText(`${parts.totals.case.parts} parts`)
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

test(`${J7_1} (J7.1) control: a stale case record shows the contract sentence (the absence check above can fail)`, async ({ page }) => {
  const w = await boot(page)
  await page.route('**/data/manifest.json', async (route) => {
    const res = await route.fetch()
    const m = (await res.json()) as Manifest
    m.records['case'] = { ...m.records['case']!, status: 'stale', basis_version: 'A1-draft', current_version: 'A9' }
    await route.fulfill({ response: res, json: m })
  })
  await toCase(page)
  await expect(byTestId(page, 'case', 'state-banner'), 'a stale case record shows no banner').toContainText('Made for design A1-draft; the design is now A9.')
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

test(`${J7_2} (J7.2) Case: a part row opens its card with the part's id and the line's words from the record`, async ({ page }) => {
  const w = await boot(page)
  const c = caseRec()
  const parts = bundleRecord<Parts>('parts.json')
  await toCase(page)

  const rows = byTestId(page, 'case', 'part-row')
  const caseLines = parts.lines.filter((l) => l.bom === 'case' && l.part_ids.some((id) => c.part_ids.includes(id)))
  await expect(rows, 'the parts list shows a different number of rows than the case lines of the record').toHaveCount(caseLines.length)
  await expect(byTestId(page, 'case', 'part-card'), 'a part card is open before any click').toHaveCount(0)

  // the pins: the record names them by node; their part ids give the lines, and the row of each opens that card
  const pinNodes = c.glb!.nodes.filter((n) => /^pin_P\d/.test(n.name) && n.part_ids.length === 1)
  expect(pinNodes.length, 'control: the case record has no pin nodes with a part id').toBeGreaterThanOrEqual(4)
  const pinLine = parts.lines.find((l) => l.part_ids.includes(pinNodes[0]!.part_ids[0]!))
  expect(pinLine, 'control: no parts-list line for the first pin').toBeTruthy()
  const line = pinLine!
  const pinId = process.env.J7_PIN ?? line.part_ids[0]!

  const row = rows.and(page.locator(`[data-part-id="${pinId}"]`))
  await expect(row, `no row for ${pinId} in the case parts list`).toHaveCount(1)
  await row.locator('button').click()
  const card = byTestId(page, 'case', 'part-card')
  await expect(card, 'a click on the row opened no part card (case.part-card)').toHaveCount(1)
  await expect(card, "the card shows another part than the row's").toHaveAttribute('data-part-id', pinId)
  await expect(card.locator('.pc-h'), 'the card heading is neither the part note nor the parts-list item').toHaveText(headingOf(pinId, line))
  await expect(card, 'the card does not name the part reference and the case').toContainText(`Part · ${pinId.split(':')[1]} · case`)
  await expect(page, 'the URL does not keep the selection (?part=)').toHaveURL(new RegExp(`part=${encodeURIComponent(pinId).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`))
  await expect(byTestId(page, 'case', 'selected-line'), 'the parts-list line of the selection is not shown').toContainText(line.refs.join(' '))
  await expect(row, 'the opened row is not marked selected').toHaveAttribute('data-selected', 'true')

  // other rows open their own card, not the first one's (one row per parts-list line: its first part id)
  const others = caseLines.filter((l) => l !== line).slice(0, 3)
  expect(others.length, 'control: the case has no other parts-list line to click').toBe(3)
  for (const l of others) {
    const id = l.part_ids[0]!
    await rows.and(page.locator(`[data-part-id="${id}"]`)).locator('button').click()
    await expect(card, `the card of ${id} shows another part`).toHaveAttribute('data-part-id', id)
    await expect(card.locator('.pc-h'), `the card heading of ${id} is wrong`).toHaveText(headingOf(id, l))
  }
  // close it
  await page.getByRole('button', { name: 'Close part card' }).click()
  await expect(card, 'the part card stayed open after "Close part card"').toHaveCount(0)
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

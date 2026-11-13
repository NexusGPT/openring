// J3: Check where the design stands (docs/JOURNEYS.md J3.1 to J3.3; rows J3#1 to J3#3 of docs/TEST-PLAN.md section 3).
// Written from the signed journey table, never from a built screen. Every expected value is read from the
// bundle under test (EXPLORER_BUNDLE, default the frozen copy). Headless only.
// Element ids follow docs/CONTRACT.md section 6; the ids this file needs are listed in docs/lanes/journeys-a.md.
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect as baseExpect, test, type Locator, type Page } from '@playwright/test'
import { AREA_PILL_WORDS, banner } from '../src/contract/vocabulary'
import { FIXTURE_DATA, blockOffline, byTestId, watchConsole } from '../tests/support'

const expect = baseExpect.configure({ timeout: 6_000 })
test.describe.configure({ timeout: 40_000 })

const J3_1 = "J3#1"
const J3_2 = "J3#2"
const J3_3 = "J3#3"

const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
function bundleRecord<T>(file: string): T {
  if (!existsSync(join(BUNDLE, 'manifest.json'))) {
    throw new Error(`journey setup: no bundle at ${BUNDLE} (manifest.json missing). Set EXPLORER_BUNDLE to a built bundle folder: the frozen copy .cache/fixture-99dfb85/data, or public/data after npm run collect.`)
  }
  const p = join(BUNDLE, file)
  if (!existsSync(p)) throw new Error(`journey setup: record ${file} is missing from the bundle ${BUNDLE}; the bundle is not complete for this journey`)
  return JSON.parse(readFileSync(p, 'utf8')) as T
}
interface Area { id: string; state: string }
interface Supplier { id: string; item: string; who: string; ask: string }
interface Open {
  supplier_requests: Supplier[]
  bench_tests: { id: string }[]
  risks: { id: string }[]
  decisions: { date: string; quote: string }[]
}
interface Board { routed: boolean; missing: string[]; placements: { name: string; side: 'top' | 'bottom' }[] }
const areas = () => bundleRecord<{ areas: Area[] }>('areas.json').areas
const openItems = () => bundleRecord<Open>('open.json')
const board = () => bundleRecord<Board>('board/index.json')

const norm = (s: string) => s.replace(/\s+/g, ' ').trim().toLowerCase()
const tile = (page: Page, area: string): Locator => byTestId(page, 'home', 'area-tile').and(page.locator(`[data-area="${area}"]`))

/** Click a tab of the top bar; an absent tab fails at once and says so. */
async function clickTab(page: Page, id: string): Promise<void> {
  const t = byTestId(page, 'app', `tab-${id}`)
  await expect(t, `the top bar has no entry '${id}' (app.tab-${id})`).toBeVisible()
  await t.click()
}

/** Click the Home tile of one area; an absent tile fails at once and says so (no 40 s click wait). */
async function clickTile(page: Page, area: string): Promise<void> {
  await expect(tile(page, area), `Home has no tile for area '${area}' (home.area-tile[data-area=${area}])`).toBeVisible({ timeout: 15_000 })
  await tile(page, area).click()
}

test(`${J3_1} (J3.1) Home: 8 tiles read the state of each area; a click on Board goes to Board`, async ({ page }) => {
  const w = watchConsole(page)
  await blockOffline(page, w)
  // arrive by the top bar "Home" (from another screen), not by typing the Home address
  await page.goto('/parts')
  await clickTab(page, 'home')
  await expect(page, 'the top bar "Home" did not lead to the Home address').toHaveURL(/\/(\?.*|#.*)?$/)

  const a = areas()
  const tiles = byTestId(page, 'home', 'area-tile')
  await expect(tiles, 'Home does not show the area tiles (home.area-tile)').toHaveCount(a.length)
  for (const area of a) {
    const pill = tile(page, area.id).locator('[data-testid="home.state-pill"]')
    await expect(pill, `tile '${area.id}' has no single state pill`).toHaveCount(1)
    await expect(pill, `tile '${area.id}' does not read the state of areas.json`).toHaveText(area.state)
    expect(AREA_PILL_WORDS, `the bundle state '${area.state}' is not in the vocabulary`).toContain(area.state)
  }
  // the four known states are the only words on tiles
  const texts = await tiles.locator('[data-testid="home.state-pill"]').allInnerTexts()
  for (const t of texts) expect(AREA_PILL_WORDS).toContain(t.trim())

  await clickTile(page, 'board')
  await expect(page, 'clicking the Board tile did not go to /board').toHaveURL(/\/board(\/|\?|#|$)/)
  await expect(byTestId(page, 'app', 'tab-board')).toHaveAttribute('aria-current', 'page')
})

test(`${J3_2} (J3.2) Board: a banner says "not routed" and names what is missing; the plan shows every placed part`, async ({ page }) => {
  const w = watchConsole(page)
  await blockOffline(page, w)
  await page.goto('/')
  await clickTile(page, 'board')
  await expect(page, 'the Board tile did not go to /board').toHaveURL(/\/board(\/|\?|#|$)/)

  // first what the screen shows, then what the bundle says it must show
  const marks = byTestId(page, 'board', 'plan-mark')
  await expect(marks.first(), 'the Board screen shows no placement plan (board.plan-mark)').toBeVisible()
  const b = board()
  const bn = byTestId(page, 'board', 'state-banner')
  if (b.routed) {
    await expect(bn.filter({ hasText: /not routed/i }), 'a routed board must not carry the "not routed" banner').toHaveCount(0)
  } else {
    await expect(bn, 'the board is not routed but no banner (board.state-banner) is shown: it looks ready to build').toBeVisible()
    const expected = banner({ kind: 'board-not-routed', missing: b.missing })
    expect(norm(await bn.innerText())).toContain(norm(expected.sentence))
    await expect(bn).toContainText(/not routed/i)
    expect(b.missing.length, 'control: the bundle names nothing missing for an unrouted board').toBeGreaterThan(0)
    for (const m of b.missing) await expect(bn, `the banner does not name '${m}'`).toContainText(m)
  }

  // the plan: one mark per placed part, as many as the bundle lists, on both sides
  await expect(marks).toHaveCount(b.placements.length)
  for (const side of ['top', 'bottom'] as const) {
    const n = b.placements.filter((p) => p.side === side).length
    await expect(marks.and(page.locator(`[data-side="${side}"]`)), `plan marks on the ${side} side`).toHaveCount(n)
  }
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

test(`${J3_3} (J3.3) Open items: the chip "waiting on a supplier" shortens the list to the supplier requests`, async ({ page }) => {
  const w = watchConsole(page)
  await blockOffline(page, w)
  await page.goto('/')
  await clickTab(page, 'open')
  await expect(page, 'the top bar "Open items" did not go to /open').toHaveURL(/\/open(\/|\?|#|$)/)

  const rows = byTestId(page, 'open', 'item-row')
  await expect(rows.first(), 'Open items shows no rows (open.item-row)').toBeVisible()
  const o = openItems()
  const all = o.supplier_requests.length + o.bench_tests.length + o.risks.length + o.decisions.length
  await expect(rows).toHaveCount(all)
  await expect(byTestId(page, 'open', 'group-heading'), 'the list has 4 groups: supplier requests, bench tests, risks, decisions').toHaveCount(4)

  // decisions carry their date and are listed newest first
  const dates = await byTestId(page, 'open', 'item-row').and(page.locator('[data-group="decision"]')).evaluateAll((els) => els.map((e) => e.getAttribute('data-date') ?? ''))
  expect(dates, 'decision rows must carry data-date').toEqual([...o.decisions.map((d) => d.date)].sort().reverse())

  const chip = byTestId(page, 'open', 'filter-chip').filter({ hasText: /waiting on a supplier/i })
  await expect(chip, 'no chip "waiting on a supplier" (open.filter-chip)').toHaveCount(1)
  expect(o.supplier_requests.length, 'control: the bundle has no supplier request').toBeGreaterThan(0)
  expect(all, 'control: the unfiltered list is not longer than the supplier list').toBeGreaterThan(o.supplier_requests.length)
  await chip.click()
  await expect(rows, 'the filter did not shorten the list to the supplier requests').toHaveCount(o.supplier_requests.length)
  for (const s of o.supplier_requests) {
    const row = rows.and(page.locator(`[data-id="${s.id}"]`))
    await expect(row, `supplier request ${s.id} is not listed after the filter`).toHaveCount(1)
    await expect(row.locator('[data-testid="open.item-who"]')).toHaveText(s.who)
    await expect(row.locator('[data-testid="open.item-ask"]')).toContainText(s.ask)
  }
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

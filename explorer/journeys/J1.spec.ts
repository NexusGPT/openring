// J1: See the ring and understand one part (docs/JOURNEYS.md J1.1 to J1.4; rows J1#1 to J1#4 of docs/TEST-PLAN.md section 3).
// Written from the signed journey table, never from a built screen. Every expected value is read from the
// bundle under test (EXPLORER_BUNDLE, default the frozen copy), never typed here. Headless only.
// Element ids follow docs/CONTRACT.md section 6 ('<route>.<element>'); the ids this file needs are listed in docs/lanes/journeys-a.md.
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { expect as baseExpect, test, type Locator, type Page } from '@playwright/test'
import { EXPLODE_MIN_GAP_MM } from '../src/contract/constants'
import { WORDS } from '../src/contract/vocabulary'
import { FIXTURE_DATA, blockOffline, byTestId, watchConsole, type Watch } from '../tests/support'

const expect = baseExpect.configure({ timeout: 6_000 })
test.describe.configure({ timeout: 45_000 })

const J1_1 = "J1#1"
const J1_2 = "J1#2"
const J1_3 = "J1#3"
const J1_4 = "J1#4"

// ---- bundle under test -------------------------------------------------------------------------------
const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
const CONTENT = join(dirname(fileURLToPath(import.meta.url)), '..', 'content')

function bundleRecord<T>(file: string): T {
  const p = join(BUNDLE, file)
  if (!existsSync(join(BUNDLE, 'manifest.json'))) {
    throw new Error(`journey setup: no bundle at ${BUNDLE} (manifest.json missing). Set EXPLORER_BUNDLE to a built bundle folder: the frozen copy .cache/fixture-99dfb85/data, or public/data after npm run collect.`)
  }
  if (!existsSync(p)) throw new Error(`journey setup: record ${file} is missing from the bundle ${BUNDLE}; the bundle is not complete for this journey`)
  return JSON.parse(readFileSync(p, 'utf8')) as T
}

interface Fact { id: string; label: string; value: string }
interface Area { id: string; state: string }
interface Layer { id: string; label: string; order: number }
interface Sources { raw: string; path: string | null; url: string | null; on_disk: boolean }
interface Line { part_ids: string[]; item: string; size_mm: string | null; key_figures: string | null; value: string | null; maker: string | null; maker_part_number: string | null; open_action: string | null; sources: Sources[] }
interface Note { what: string; why: string; model_names: string[] }
interface Box { min: number[]; max: number[] }

const facts = () => bundleRecord<{ facts: Fact[] }>('facts.json').facts
const areas = () => bundleRecord<{ areas: Area[] }>('areas.json').areas
const layers = () => [...bundleRecord<{ layers: Layer[] }>('placements.json').layers].sort((a, b) => a.order - b.order)
const lines = () => bundleRecord<{ lines: Line[] }>('parts.json').lines
const notes = () => (JSON.parse(readFileSync(join(CONTENT, 'part-notes.json'), 'utf8')) as { notes: Record<string, Note> }).notes
const servedPaths = () => new Set(bundleRecord<{ files: { path: string }[] }>('files.json').files.map((f) => f.path))
/** The part this journey is about: the battery cell, parts-list line BT1 (id ring:BT1). */
const CELL_ID = 'ring:BT1'
const cellLine = () => {
  const l = lines().find((x) => x.part_ids.includes(CELL_ID))
  if (!l) throw new Error(`journey setup: no parts-list line for ${CELL_ID} in ${BUNDLE}/parts.json`)
  return l
}
const cellNote = () => {
  const n = notes()[CELL_ID]
  if (!n || n.model_names.length === 0) throw new Error(`journey setup: no note with a model name for ${CELL_ID} in content/part-notes.json`)
  return n
}

// ---- page helpers ------------------------------------------------------------------------------------
const norm = (s: string) => s.replace(/\s+/g, ' ').trim().toLowerCase()
const stage = (page: Page) => byTestId(page, 'app', 'stage')
const canvas = (page: Page): Locator => stage(page).locator('canvas')
const tile = (page: Page, area: string): Locator => byTestId(page, 'home', 'area-tile').and(page.locator(`[data-area="${area}"]`))

async function boot(page: Page): Promise<Watch> {
  const w = watchConsole(page)
  await blockOffline(page, w)
  return w
}
async function stageReady(page: Page): Promise<void> {
  await expect
    .poll(() => page.evaluate(() => window.__stage?.ready === true), { timeout: 20_000, message: 'the 3D stage never reported ready: window.__stage is missing or not ready' })
    .toBe(true)
}
/** Fraction of pixels that differ between two PNGs (any channel by more than 12), or from the corner colour when b is null. */
async function pixels(page: Page, a: Buffer, b: Buffer | null): Promise<number> {
  return page.evaluate(
    async ([aa, bb]) => {
      const load = async (s: string) => {
        const bytes = Uint8Array.from(atob(s), (c) => c.charCodeAt(0))
        const bmp = await createImageBitmap(new Blob([bytes], { type: 'image/png' }))
        const c = new OffscreenCanvas(bmp.width, bmp.height)
        const g = c.getContext('2d')!
        g.drawImage(bmp, 0, 0)
        return g.getImageData(0, 0, bmp.width, bmp.height)
      }
      const A = await load(aa)
      const B = bb ? await load(bb) : null
      let n = 0
      const total = A.width * A.height
      for (let i = 0; i < total; i++) {
        const o = i * 4
        const ref = B ? [B.data[o]!, B.data[o + 1]!, B.data[o + 2]!] : [A.data[0]!, A.data[1]!, A.data[2]!]
        if (Math.abs(A.data[o]! - ref[0]!) > 12 || Math.abs(A.data[o + 1]! - ref[1]!) > 12 || Math.abs(A.data[o + 2]! - ref[2]!) > 12) n++
      }
      return n / total
    },
    [a.toString('base64'), b ? b.toString('base64') : null] as [string, string | null],
  )
}
const angleDiff = (a: number, b: number) => Math.abs(((((a - b) % 360) + 540) % 360) - 180)
interface PlacementLayer { id: string; order: number; explode?: { x: number; y: number; z: number } | 'radial' }
const placementLayers = () => [...bundleRecord<{ layers: PlacementLayer[] }>('placements.json').layers].sort((a, b) => a.order - b.order)
const boxesNow = (page: Page) => page.evaluate(() => window.__stage!.layerBoxes()) as Promise<Record<string, Box>>
const axisOf = (v: { x: number; y: number; z: number }) => {
  const c = [Math.abs(v.x), Math.abs(v.y), Math.abs(v.z)]
  const i = c.indexOf(Math.max(...c))
  return { i, sign: Math.sign([v.x, v.y, v.z][i]!) }
}
/** Each layer opens along its own direction (the bundle's explode field): a vector layer moves at least the minimum
 *  gap along it, a radial layer grows outward by at least the minimum gap, and two neighbouring layers that open
 *  along the same axis end clear of each other by the minimum gap measured along that axis. */
function checkOpening(closed: Record<string, Box>, open: Record<string, Box>): void {
  const ls = placementLayers()
  for (const l of ls) {
    const c = closed[l.id]
    const o = open[l.id]
    if (!c || !o) throw new Error(`stage layerBoxes() has no box for layer '${l.id}' listed in placements.json`)
    if (l.explode === 'radial') {
      const grow = Math.max(...[0, 1, 2].map((i) => Math.max(o.max[i]! - c.max[i]!, c.min[i]! - o.min[i]!)))
      expect(grow, `radial layer '${l.id}' grew outward by only ${grow} mm`).toBeGreaterThanOrEqual(EXPLODE_MIN_GAP_MM - 0.001)
    } else if (l.explode) {
      const { i, sign } = axisOf(l.explode)
      const centre = (b: Box) => (b.min[i]! + b.max[i]!) / 2
      const moved = (centre(o) - centre(c)) * sign
      expect(moved, `layer '${l.id}' moved only ${moved} mm along its opening direction`).toBeGreaterThanOrEqual(EXPLODE_MIN_GAP_MM - 0.001)
    }
  }
  ls.slice(1).forEach((l, k) => {
    const p = ls[k]!
    if (!p.explode || !l.explode || p.explode === 'radial' || l.explode === 'radial') return
    const a = axisOf(p.explode)
    const b = axisOf(l.explode)
    if (a.i !== b.i || a.sign !== b.sign) return
    const lo = open[p.id]!
    const hi = open[l.id]!
    const g = Math.max(lo.min[a.i]! - hi.max[a.i]!, hi.min[a.i]! - lo.max[a.i]!)
    expect(g, `layers '${p.id}' and '${l.id}' are only ${g} mm apart along their opening axis`).toBeGreaterThanOrEqual(EXPLODE_MIN_GAP_MM - 0.001)
  })
}
/** Open the ring by the control and wait until the stage has finished moving. */
async function openRing(page: Page): Promise<void> {
  await stageReady(page)
  // the open control: the end button of the slider, or the toggle "Open the ring" (pressed = already open)
  const endBtn = byTestId(page, 'inside', 'explode-open')
  const toggle = byTestId(page, 'inside', 'open-ring')
  await expect(endBtn.or(toggle), 'Inside has no control to open the ring (inside.explode-open or inside.open-ring)').toBeVisible()
  if (await endBtn.isVisible()) await endBtn.click()
  else if ((await toggle.getAttribute('aria-pressed')) !== 'true') await toggle.click()
  await expect.poll(() => page.evaluate(() => window.__stage!.explode()), { timeout: 10_000, message: 'explode() did not reach 1 after opening the ring' }).toBeGreaterThan(0.99)
  await page.waitForTimeout(300)
}

/** Click the Home tile of one area; an absent tile fails at once and says so (no 40 s click wait). */
async function clickTile(page: Page, area: string): Promise<void> {
  await expect(tile(page, area), `Home has no tile for area '${area}' (home.area-tile[data-area=${area}])`).toBeVisible({ timeout: 15_000 })
  await tile(page, area).click()
}

/** Home by its address (J1.1 only), then the tile click of J1.2. */
async function openHome(page: Page): Promise<void> {
  await page.goto('/')
}
async function goInside(page: Page): Promise<void> {
  await openHome(page)
  await clickTile(page, 'inside')
  await expect(page).toHaveURL(/\/inside(\/|\?|#|$)/)
}
async function clickNode(page: Page, node: string): Promise<void> {
  await stageReady(page)
  await expect.poll(() => page.evaluate((n) => window.__stage!.screenPos(n) !== null, node), { timeout: 10_000, message: `stage.screenPos('${node}') stayed null: the node is not on screen` }).toBe(true)
  const pos = await page.evaluate((n) => window.__stage!.screenPos(n), node)
  const box = (await canvas(page).boundingBox())!
  await page.mouse.click(box.x + pos!.x, box.y + pos!.y)
}
/** What the last click selected, read from the address: part=<id> or object=<node>. */
const picked = (page: Page) => {
  const q = new URL(page.url()).searchParams
  return q.get('part') ? `part ${q.get('part')}` : q.get('object') ? `object ${q.get('object')}` : 'nothing'
}
const card = (page: Page) => byTestId(page, 'inside', 'part-card')

// ---- J1.1 --------------------------------------------------------------------------------------------
test(`${J1_1} (J1.1) Home: the ring turns, the key numbers and the 8 area tiles read from the bundle`, async ({ page }) => {
  const w = await boot(page)
  await openHome(page)

  // sees: key numbers
  const keys = byTestId(page, 'home', 'section-numbers')
  await expect(keys, 'Home shows no key numbers section (home.section-numbers)').toBeVisible()
  const f = facts()
  expect(f.length).toBeGreaterThan(0)
  for (const fact of f) {
    const row = keys.locator(`[data-testid="home.key-number"][data-fact="${fact.id}"]`)
    await expect(row, `key number '${fact.label}' is not shown (home.key-number[data-fact=${fact.id}])`).toHaveCount(1)
    await expect(row, `key number '${fact.label}' does not read '${fact.value}'`).toContainText(fact.value)
  }
  expect(await byTestId(page, 'home', 'key-number').count(), 'fewer key-number rows than facts').toBeGreaterThanOrEqual(f.length)

  // sees: 8 area tiles, each with one pill that reads the state of the bundle
  const a = areas()
  await expect(byTestId(page, 'home', 'area-tile')).toHaveCount(a.length)
  for (const area of a) {
    const pill = tile(page, area.id).locator('[data-testid="home.state-pill"]')
    await expect(pill, `tile '${area.id}' has no single state pill`).toHaveCount(1)
    await expect(pill).toHaveText(area.state)
    if (area.state !== 'state unknown') await expect(pill).not.toHaveText(WORDS.stateUnknown)
  }

  // does: rotates the ring; sees: it turns (first the stage draws, then a 200 px drag moves it)
  await stageReady(page)
  const c = canvas(page)
  await expect(c).toBeVisible()
  const before = await c.screenshot()
  expect(await pixels(page, before, null), 'the canvas is blank: under 2 % of its pixels differ from the background').toBeGreaterThanOrEqual(0.02)
  const az0 = await page.evaluate(() => window.__stage!.azimuthDeg())
  const box = (await c.boundingBox())!
  const cx = box.x + box.width / 2
  const cy = box.y + box.height / 2
  await page.mouse.move(cx, cy)
  await page.mouse.down()
  await page.mouse.move(cx + 200, cy, { steps: 12 })
  await page.mouse.up()
  const az1 = await page.evaluate(() => window.__stage!.azimuthDeg())
  expect(angleDiff(az1, az0), 'the 200 px drag did not turn the ring by over 20 degrees').toBeGreaterThan(20)
  expect(await page.evaluate(() => window.__stage!.autoRotate), 'auto-rotate must stop after the first drag').toBe(false)
  // the ring may glide to a stop (damping); it must slow down, never keep a steady turn of its own
  const steps: number[] = []
  let last = az1
  for (let i = 0; i < 6; i++) {
    await page.waitForTimeout(500)
    const now = await page.evaluate(() => window.__stage!.azimuthDeg())
    steps.push(angleDiff(now, last))
    last = now
  }
  expect(steps[5]! < 1 || steps[5]! < steps[0]! * 0.6, `the ring keeps turning at a steady rate after the drag: degrees per half second ${steps.map((x) => x.toFixed(2)).join(', ')}`).toBe(true)
  const after = await c.screenshot()
  expect(await pixels(page, after, before), 'the picture did not change after the drag: under 1 % of pixels differ').toBeGreaterThanOrEqual(0.01)

  // visible failure words never appear on a good bundle; no console error
  await expect(page.getByText(WORDS.runCollect)).toHaveCount(0)
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

// ---- J1.2 --------------------------------------------------------------------------------------------
test(`${J1_2} (J1.2) Inside: the slider "open it up" separates the layers`, async ({ page }) => {
  const w = await boot(page)
  await openHome(page)
  await clickTile(page, 'inside')
  await expect(page, 'the Inside tile did not lead to /inside').toHaveURL(/\/inside(\/|\?|#|$)/)

  const slider = byTestId(page, 'inside', 'explode-slider')
  await expect(slider, 'Inside has no slider (inside.explode-slider)').toBeVisible()
  await expect(slider, 'the slider is not named "Open it up"').toHaveAccessibleName('Open it up')
  await stageReady(page)
  expect(await page.evaluate(() => window.__stage!.explode())).toBeLessThan(0.05)
  const closedBoxes = await boxesNow(page)
  const c = canvas(page)
  const closed = await c.screenshot()

  const sb = (await slider.boundingBox())!
  await page.mouse.move(sb.x + 2, sb.y + sb.height / 2)
  await page.mouse.down()
  await page.mouse.move(sb.x + sb.width - 2, sb.y + sb.height / 2, { steps: 12 })
  await page.mouse.up()
  await expect.poll(() => page.evaluate(() => window.__stage!.explode()), { message: 'explode() did not reach 1 after dragging the slider to its end' }).toBeGreaterThan(0.99)
  await page.waitForTimeout(300)

  checkOpening(closedBoxes, await boxesNow(page))
  expect(await pixels(page, await c.screenshot(), closed), 'the opened picture differs from the closed one by under 2 %').toBeGreaterThanOrEqual(0.02)

  // the layer list names every layer of the bundle; a layer with no model is a text row
  const rows = byTestId(page, 'inside', 'layer-row')
  await expect(rows).toHaveCount(layers().length)
  for (const l of layers()) await expect(rows.filter({ hasText: l.label }), `layer '${l.label}' is not listed`).toHaveCount(1)
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

// ---- J1.3 --------------------------------------------------------------------------------------------
test(`${J1_3} (J1.3) Inside: a click on the cell highlights it and opens its part card`, async ({ page }) => {
  await boot(page)
  await goInside(page)
  await openRing(page)
  const note = cellNote()
  const node = note.model_names[0]!
  const c = canvas(page)
  await page.mouse.move(0, 0)
  const pos0 = (await page.evaluate((n) => window.__stage!.screenPos(n), node)) ?? { x: 0, y: 0 }
  const box = (await c.boundingBox())!
  const clip = { x: Math.max(0, box.x + pos0.x - 40), y: Math.max(0, box.y + pos0.y - 40), width: 80, height: 80 }
  const around0 = await page.screenshot({ clip })

  await clickNode(page, node)
  const cd = card(page)
  await expect(cd, 'no part card opened after the click on the cell (inside.part-card)').toBeVisible()
  await expect(page).toHaveURL(new RegExp(`part=${encodeURIComponent(CELL_ID)}`))
  await expect(cd).toHaveAttribute('data-part-id', CELL_ID)

  // what the card says, from the bundle and the notes: plain words, why, size numbers, key figures, the open ask
  const text = norm((await cd.innerText()) ?? '')
  const l = cellLine()
  expect(text, 'card lacks the note "what"').toContain(norm(note.what))
  expect(text, 'card lacks the note "why"').toContain(norm(note.why))
  for (const n of (l.size_mm ?? '').match(/\d+(?:\.\d+)?/g) ?? []) expect(text, `card lacks the size number ${n}`).toMatch(new RegExp(`(^|[^\\d.])${n.replace('.', '\\.')}([^\\d]|$)`))
  if (l.key_figures) expect(text, 'card lacks the key figures').toContain(norm(l.key_figures))
  if (l.open_action) expect(text, 'card lacks the open action').toContain(norm(l.open_action).slice(0, 40))
  expect(text, 'the cell must have a parts-list line').not.toContain(WORDS.noPartsLine)

  // exact data (maker part number, value) is one click below and closed by default
  if (l.maker_part_number) await expect(cd.getByText(l.maker_part_number)).toHaveCount(0)
  await byTestId(page, 'inside', 'part-card-exact-toggle').click()
  const exact = byTestId(page, 'inside', 'part-card-exact')
  await expect(exact).toBeVisible()
  if (l.value) await expect(exact).toContainText(l.value)
  if (l.maker_part_number) await expect(exact).toContainText(l.maker_part_number)

  // the cell is highlighted on the canvas: the pixels around it changed (mouse parked away from it)
  await page.mouse.move(0, 0)
  await page.waitForTimeout(400)
  expect(await pixels(page, await page.screenshot({ clip }), around0), 'the pixels around the cell did not change: no highlight').toBeGreaterThanOrEqual(0.02)

  // positive control for the absence above: an object with no parts-list line DOES show the words
  const model = bundleRecord<{ nodes: { name: string; part_ids: string[] }[] }>('ring-model.json')
  const linkedByNotes = new Set(Object.values(notes()).flatMap((n) => n.model_names))
  const unlinked = model.nodes.filter((n) => n.part_ids.length === 0 && !linkedByNotes.has(n.name)).map((n) => n.name)
  let shown = false
  const tried: string[] = []
  // the ring is open now; if no unlinked object is on screen there, close it and try again
  for (const mode of ['open', 'closed'] as const) {
    if (shown) break
    if (mode === 'closed') {
      await byTestId(page, 'inside', 'explode-closed').click()
      await expect.poll(() => page.evaluate(() => window.__stage!.explode()), { timeout: 10_000 }).toBeLessThan(0.01)
      await page.waitForTimeout(300)
    }
    for (const n of unlinked.slice(0, 8)) {
      const p = await page.evaluate((x) => window.__stage!.screenPos(x), n)
      if (!p) {
        tried.push(`${mode}: ${n} -> not on screen`)
        continue
      }
      await page.mouse.click(box.x + p.x, box.y + p.y)
      await page.waitForTimeout(900)
      tried.push(`${mode}: ${n} -> ${picked(page)}`)
      if ((await byTestId(page, 'inside', 'part-card-no-line').count()) > 0) {
        shown = true
        break
      }
    }
  }
  const onScreen = tried.filter((t) => !t.endsWith('not on screen'))
  if (!shown && onScreen.length === 0) {
    test.info().annotations.push({ type: 'not-exercised', description: `no object without a parts-list line is on screen in this bundle (${tried.join('; ') || 'none exist'}): the no-line control is skipped; the card text checks above are the positive control` })
  } else {
    expect(shown, `control: clicking an object with no parts-list line never showed "${WORDS.noPartsLine}". Clicked (node -> what the screen selected): ${tried.join('; ')}`).toBe(true)
  }
})

// ---- J1.4 --------------------------------------------------------------------------------------------
test(`${J1_4} (J1.4) Inside: the source link of the card opens the file in a new tab`, async ({ page, context }) => {
  await boot(page)
  await goInside(page)
  await openRing(page)
  const note = cellNote()
  await clickNode(page, note.model_names[0]!)
  const cd = card(page)
  await expect(cd, 'no part card opened (inside.part-card)').toBeVisible()
  const served = servedPaths()
  const src = cellLine().sources.find((s) => s.path && s.on_disk && served.has(s.path))
  expect(src, `control: ${CELL_ID} has no source that is on disk and listed in files.json`).toBeTruthy()

  const toggle = byTestId(page, 'inside', 'part-card-exact-toggle')
  if ((await toggle.getAttribute('aria-expanded')) !== 'true') await toggle.click()
  const link = cd.locator(`a[href*="${src!.path!}"]`)
  await expect(link, `no link to ${src!.path} in the card`).toHaveCount(1)
  await expect(link).toHaveAttribute('target', '_blank')

  const [popup] = await Promise.all([context.waitForEvent('page', { timeout: 8_000 }), link.click()])
  await popup.waitForLoadState('domcontentloaded')
  expect(popup.url()).toContain(`/files/${src!.path!}`)
  const res = await page.request.get(popup.url())
  expect(res.status(), `the source answers ${res.status()}`).toBe(200)
  const body = await res.body()
  expect(body.length, 'the source file is empty').toBeGreaterThan(0)
  const ctype = res.headers()['content-type'] ?? ''
  expect(ctype, 'the source answered with an HTML page, not the file').not.toContain('text/html')

  // failure branch: a source that is not served shows greyed with the vocabulary reason and opens no tab
  const unserved = lines().find((x) => x.sources.some((s) => !s.on_disk || (s.path && !served.has(s.path))) && x.part_ids.some((id) => (notes()[id]?.model_names.length ?? 0) > 0))
  if (unserved) {
    const id = unserved.part_ids.find((i) => (notes()[i]?.model_names.length ?? 0) > 0)!
    // 2026-11-10 (lead's ruling): the part is chosen through the Inside panel as a user who cannot see it does
    // (its layer row, then the part in the list), not by a 3D click: the board covers the parts hung under it.
    // J1#3 proves the 3D click on the cell. Every assertion on the card below is unchanged.
    const nodeName = notes()[id]!.model_names[0]!
    const layer = bundleRecord<{ placements: { name: string; layer: string }[] }>('placements.json').placements.find((x) => x.name === nodeName)?.layer
    expect(layer, `control: placements.json has no layer for '${nodeName}'`).toBeTruthy()
    const row = byTestId(page, 'inside', 'layer-row').and(page.locator(`[data-layer="${layer}"]`))
    // with a card open the list is replaced by "All layers": go back to the list first, as a user would
    if ((await row.count()) === 0) await byTestId(page, 'inside', 'card-close').click()
    await expect(row, `Inside has no layer row '${layer}' (inside.layer-row[data-layer])`).toBeVisible()
    if ((await row.getAttribute('aria-pressed')) !== 'true') await row.click()
    const entry = byTestId(page, 'inside', 'layer-part').and(page.locator(`[data-part-id="${id}"]`))
    await expect(entry.first(), `the layer '${layer}' lists no object for ${id}`).toBeVisible()
    await entry.first().click()
    await expect(card(page), `choosing ${id} in the layer list did not open its card`).toHaveAttribute('data-part-id', id)
    const t2 = byTestId(page, 'inside', 'part-card-exact-toggle')
    if ((await t2.getAttribute('aria-expanded')) !== 'true') await t2.click()
    const off = card(page).locator('[aria-disabled="true"]')
    await expect(off.first()).toContainText(WORDS.notOnDisk)
  } else {
    test.info().annotations.push({ type: 'not-exercised', description: 'no model-linked part with an unserved source in this bundle: greyed-link branch skipped' })
  }
})

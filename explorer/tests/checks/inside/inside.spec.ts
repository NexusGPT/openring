// Checks of the Inside screen (inside-C01 .. C32, layout C: the ring above, the drawing below). Headless. Data is read from the bundle named by
// EXPLORER_BUNDLE (default public/data); no ring value is written here, every name comes from the files.
// Set INSIDE_BASE_URL to run against a dev server other than the one in the Playwright config.
import { expect, test, type Page } from '@playwright/test'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { EXPLODE_MIN_GAP_MM } from '../../../src/contract/constants'
import { EXPLORER_ROOT, waitStageReady, watchConsole } from '../../support'

const BUNDLE = process.env.EXPLORER_BUNDLE ?? join(EXPLORER_ROOT, 'public', 'data')
const json = (f: string) => JSON.parse(readFileSync(join(BUNDLE, f), 'utf8'))
const notes: Record<string, { what: string; model_names: string[] }> = JSON.parse(
  readFileSync(join(EXPLORER_ROOT, 'content', 'part-notes.json'), 'utf8'),
).notes
type Dir = { x: number; y: number; z: number } | 'radial' | undefined
const placements = json('placements.json') as { layers: { id: string; label: string; explode?: Dir }[]; placements: { name: string; layer: string }[] }
const parts = json('parts.json') as { lines: { bom: string; item: string; maker: string | null; part_ids: string[]; refs: string[] }[] }

if (process.env.INSIDE_BASE_URL) test.use({ baseURL: process.env.INSIDE_BASE_URL })
const T = (page: Page, id: string) => page.getByTestId(`inside.${id}`)
const open = async (page: Page, query = '') => {
  await page.goto(`/inside${query}`)
  await waitStageReady(page)
}
const linkedObject = (): { name: string; id: string } => {
  for (const p of placements.placements) {
    const id = Object.keys(notes).find((k) => k.startsWith('ring:') && notes[k]?.model_names.includes(p.name))
    if (id) return { name: p.name, id }
  }
  throw new Error('no linked object in the bundle')
}
const frame = async (page: Page) => (await page.locator('[data-testid="app.stage"]').screenshot()).toString('base64')

type Boxes = Record<string, { min: number[]; max: number[] }>
const boxes = (page: Page) => page.evaluate(() => window.__stage?.layerBoxes() as Boxes)
const settle = (page: Page, v: number) => page.waitForFunction((x) => Math.abs((window.__stage?.explode() ?? -1) - x) < 0.01, v, { timeout: 8000 })
const gapOf = (a: Boxes[string], b: Boxes[string]) =>
  Math.max(...[0, 1, 2].flatMap((i) => [(b.min[i] ?? 0) - (a.max[i] ?? 0), (a.min[i] ?? 0) - (b.max[i] ?? 0)]))

test('inside-C01 the one control opens the ring and closes it again', async ({ page }) => {
  const w = watchConsole(page)
  await open(page)
  const closed = await boxes(page)
  const f0 = await frame(page)
  await T(page, 'open-ring').click()
  await settle(page, 1)
  await page.waitForTimeout(400)
  const open1 = await boxes(page)
  expect(await frame(page)).not.toBe(f0)
  // every layer moved, and each pair of neighbours moved apart along z (the opening is visible in the numbers)
  for (const [id, c] of Object.entries(closed)) {
    const o = open1[id]
    const moved = [0, 1, 2].some((i) => Math.abs((o?.min[i] ?? 0) - (c.min[i] ?? 0)) > 0.05 || Math.abs((o?.max[i] ?? 0) - (c.max[i] ?? 0)) > 0.05)
    expect(moved, `layer ${id} moved`).toBe(true)
  }
  for (const [a, b] of zPairs()) expect(gapOf(open1[b] as Boxes[string], open1[a] as Boxes[string]), `${a}/${b}`).toBeGreaterThan(gapOf(closed[b] as Boxes[string], closed[a] as Boxes[string]))
  await expect(T(page, 'open-ring')).toHaveText('Close the ring')
  await T(page, 'open-ring').click()
  await settle(page, 0)
  await page.waitForTimeout(400)
  const back = await boxes(page)
  for (const [id, b] of Object.entries(closed))
    for (let i = 0; i < 3; i++) {
      expect(Math.abs((back[id]?.min[i] ?? 99) - (b.min[i] ?? 0)), `${id} min ${i}`).toBeLessThan(0.05)
      expect(Math.abs((back[id]?.max[i] ?? 99) - (b.max[i] ?? 0)), `${id} max ${i}`).toBeLessThan(0.05)
    }
  expect(w.errors).toEqual([])
})

/** Neighbouring layers (record order) that both open along a z vector: a radial layer wraps the others and has no z gap. */
function zPairs(): [string, string][] {
  const out: [string, string][] = []
  const L = placements.layers
  for (let i = 1; i < L.length; i++) {
    const a = L[i - 1], b = L[i]
    if (a && b && typeof a.explode === 'object' && typeof b.explode === 'object' && a.explode.z * b.explode.z > 0) out.push([a.id, b.id])
  }
  return out
}

test('inside-C12 neighbouring layers that open along z end at least EXPLODE_MIN_GAP_MM apart', async ({ page }) => {
  await open(page)
  await T(page, 'open-ring').click()
  await settle(page, 1)
  await page.waitForTimeout(400)
  const o = await boxes(page)
  const pairs = zPairs()
  expect(pairs.length).toBeGreaterThan(0)
  for (const [a, b] of pairs) expect(gapOf(o[b] as Boxes[string], o[a] as Boxes[string]), `gap ${a} / ${b}`).toBeGreaterThanOrEqual(EXPLODE_MIN_GAP_MM - 0.05)
})

test('inside-C02 the control works from the keyboard and says what it will do', async ({ page }) => {
  await open(page)
  const b = T(page, 'open-ring')
  await expect(b).toHaveText('Open the ring')
  await b.focus()
  await page.keyboard.press('Enter')
  await page.waitForFunction(() => (window.__stage?.explode() ?? 0) > 0.95)
  await expect(b).toHaveText('Close the ring')
  await expect(b).toHaveAttribute('aria-pressed', 'true')
})

test('inside-C03 layer rows equal the layers of the record, a click isolates the layer', async ({ page }) => {
  await open(page)
  const rows = T(page, 'layer-row')
  await expect(rows).toHaveCount(placements.layers.length)
  // outside to inside: the record's order reversed (the record runs from the body up to the glass)
  for (const [i, l] of [...placements.layers].reverse().entries()) {
    const n = placements.placements.filter((p) => p.layer === l.id).length
    await expect(rows.nth(i)).toContainText(String(n))
    await expect(rows.nth(i)).toHaveAttribute('data-layer', l.id)
    await rows.nth(i).click()
    await page.waitForFunction((id) => window.__stage?.isolatedLayer() === id, l.id)
  }
  await T(page, 'layers-all').click()
  await page.waitForFunction(() => window.__stage?.isolatedLayer() === null)
})

test('inside-C04 a part chosen in the layer list opens its card; the URL keeps it over a reload', async ({ page }) => {
  await open(page)
  const { name, id } = linkedObject()
  const layer = placements.placements.find((p) => p.name === name)?.layer ?? ''
  await page.locator(`[data-testid="inside.layer-row"][data-layer="${layer}"]`).click()
  await page.locator(`[data-testid="inside.layer-part"][data-object="${name}"]`).click()
  expect(decodeURIComponent(new URL(page.url()).search)).toContain(`part=${id}`)
  const card = T(page, 'part-card')
  await expect(card).toHaveAttribute('data-part-id', id)
  await expect(card).toContainText(notes[id]?.what ?? '')
  await page.reload()
  await waitStageReady(page)
  await expect(T(page, 'part-card')).toHaveAttribute('data-part-id', id)
})

test('inside-C05 an object no parts-list line names says so; a part id with no line says so', async ({ page }) => {
  await open(page, '?object=made_up_object_name')
  await expect(T(page, 'part-card-no-line')).toHaveText('no parts-list line for this object')
  await open(page, '?part=ring%3AZZ-NO-SUCH-REF')
  await expect(T(page, 'part-card')).toBeVisible()
  await expect(T(page, 'part-card-no-line')).toHaveText('no parts-list line for this object')
})

test('inside-C06 search: a maker word lists the line, case and accents do not matter, Enter selects', async ({ page }) => {
  await open(page)
  const line = parts.lines.find((l) => l.bom === 'ring' && l.maker)
  expect(line).toBeTruthy()
  const word = (line?.maker ?? '').split(/[\s(]/)[0] ?? ''
  const search = T(page, 'search')
  const ids = async () => T(page, 'search-result').evaluateAll((els) => els.map((e) => e.getAttribute('data-part-id')))
  await search.fill(word.toUpperCase())
  const upper = await ids()
  expect(upper).toContain(line?.part_ids[0])
  await search.fill(word.toLowerCase())
  expect(await ids()).toEqual(upper)
  expect(upper.length).toBeLessThanOrEqual(8)
  const first = upper[0] ?? ''
  await search.press('Enter')
  expect(decodeURIComponent(new URL(page.url()).search)).toContain(`part=${first}`)
  await expect(T(page, 'part-card')).toHaveAttribute('data-part-id', first)
  await expect(search).toHaveCount(0) // the part frame replaces the list frame; the text was cleared on choosing
})

test('inside-C07 search: a reference lists its line; odd texts never throw and never leave the list blank', async ({ page }) => {
  const w = watchConsole(page)
  await open(page)
  const line = parts.lines.find((l) => l.bom === 'ring' && l.refs.length)
  const ref = line?.refs[0] ?? ''
  const search = T(page, 'search')
  await search.fill(ref.toLowerCase())
  await expect(T(page, 'search-result').first()).toBeVisible()
  expect(await T(page, 'search-result').evaluateAll((els) => els.map((e) => e.getAttribute('data-part-id')))).toContain(line?.part_ids[0])
  for (const text of ['D+', '(', '[', '\\', '*', 'Würth', 'zzzzzzzz-no-such-part']) {
    await search.fill(text)
    const n = await T(page, 'search-result').count()
    if (n === 0) await expect(T(page, 'search-empty')).toContainText('Nothing found')
    else expect(n).toBeLessThanOrEqual(8)
  }
  expect(w.errors).toEqual([])
})

test('inside-C08 no page scroll at 1512 x 982 and the panel holds the screen', async ({ page }) => {
  await page.setViewportSize({ width: 1512, height: 982 })
  await open(page)
  await T(page, 'layer-row').first().click()
  const m = await page.evaluate(() => ({ sh: document.documentElement.scrollHeight, ih: innerHeight, sw: document.documentElement.scrollWidth, iw: innerWidth }))
  expect(m.sh).toBeLessThanOrEqual(m.ih)
  expect(m.sw).toBeLessThanOrEqual(m.iw)
  // the panel scrolls up and down by itself, never sideways
  const panel = await page.getByTestId('app.panel-body').evaluate((e) => ({ sw: e.scrollWidth, cw: e.clientWidth }))
  expect(panel.sw).toBeLessThanOrEqual(panel.cw)
})

const resourceNoise = (e: string) => /404|Failed to load resource/.test(e)

test('inside-C09 empty bundle: an honest banner, the panel is not empty, no script error', async ({ page }) => {
  const w = watchConsole(page)
  await page.route(/\/(data\/[^?]*\.(json|glb|zip)|content\/part-notes\.json)(\?.*)?$/, (r) => r.fulfill({ status: 404, contentType: 'application/json', body: '{}' }))
  await page.goto('/inside')
  const banner = T(page, 'state-banner')
  await expect(banner.first()).toContainText('Not built yet.')
  await expect(banner.first()).toContainText('npm run collect')
  await expect(T(page, 'panel')).toBeVisible()
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(T(page, 'hint')).toBeVisible()
  expect(w.errors.filter((e) => !resourceNoise(e))).toEqual([])
})

test('inside-C10 stale placements: the banner says so in words and the layers stay on screen', async ({ page }) => {
  await page.route(/\/data\/manifest\.json/, async (r) => {
    const res = await r.fetch()
    const m = await res.json()
    m.records['part-placements'] = { ...m.records['part-placements'], status: 'stale', basis_version: 'A3', current_version: 'A5' }
    await r.fulfill({ response: res, json: m })
  })
  await page.goto('/inside')
  await expect(T(page, 'state-banner').first()).toContainText('Made for design A3; the design is now A5.')
  await expect(T(page, 'layer-row')).toHaveCount(placements.layers.length)
  await expect(T(page, 'panel')).toHaveAttribute('data-dimmed', 'true')
})

test('inside-C11 a click on the stage selects the part under it', async ({ page }) => {
  await open(page)
  const ring = json('ring-model.json') as { nodes: { name: string; layer: string | null; part_ids: string[] }[] }
  const tried: string[] = []
  for (const n of ring.nodes.filter((x) => x.part_ids.length && x.layer)) {
    await page.evaluate(() => { history.pushState(null, '', '/inside'); dispatchEvent(new PopStateEvent('popstate')) })
    await page.locator(`[data-testid="inside.layer-row"][data-layer="${n.layer}"]`).click()
    await page.waitForFunction((l) => window.__stage?.isolatedLayer() === l, n.layer)
    await page.waitForTimeout(900)
    const pos = await page.evaluate((name) => window.__stage?.screenPos(name) ?? null, n.name)
    if (!pos) continue
    const top = await page.locator('[data-testid="app.stage"]').boundingBox()
    await page.mouse.click((top?.x ?? 0) + pos.x, (top?.y ?? 0) + pos.y)
    await page.waitForTimeout(250)
    const got = new URLSearchParams(new URL(page.url()).search).get('part')
    tried.push(`${n.name}->${got}`)
    if (got && n.part_ids.includes(got)) {
      await expect(T(page, 'part-card')).toHaveAttribute('data-part-id', got)
      return
    }
  }
  throw new Error(`no click on the stage selected the part under it: ${tried.join(', ')}`)
})

/** Records, from now on, whether the card slot ever went to its leave phase (a MutationObserver sees a 160 ms phase a slow frame loop would miss). */
const watchLeave = (page: Page) => page.evaluate(() => {
  const w = window as unknown as { __sawOut: boolean }
  w.__sawOut = false
  new MutationObserver(() => { if (document.querySelector('.in-pres[data-phase="out"]')) w.__sawOut = true }).observe(document.body, { subtree: true, attributes: true, childList: true })
})
const sawLeave = (page: Page) => page.waitForFunction(() => (window as unknown as { __sawOut: boolean }).__sawOut, undefined, { timeout: 8000 })
const css = (page: Page, sel: string, props: string[], pseudo?: string) =>
  page.locator(sel).first().evaluate((e, a) => { const cs = getComputedStyle(e, a.pseudo ?? null); return Object.fromEntries(a.props.map((p) => [p, cs.getPropertyValue(p)])) }, { props, pseudo })
const select = async (page: Page) => {
  const { id } = linkedObject()
  await page.goto(`/inside?part=${encodeURIComponent(id)}`)
  await expect(T(page, 'part-card')).toBeVisible()
  return id
}

test('inside-C13 the control eases the ring fully open and fully closed, and its words follow', async ({ page }) => {
  await open(page)
  const b = T(page, 'open-ring')
  await b.click()
  await page.waitForFunction(() => (window.__stage?.explode() ?? 0) > 0.95)
  await expect(b).toHaveText('Close the ring')
  await b.click()
  await page.waitForFunction(() => (window.__stage?.explode() ?? 1) < 0.05)
  await expect(b).toHaveText('Open the ring')
})

test('inside-C14 a layer click opens a closed ring by easing (a value between 0 and 1 is seen)', async ({ page }) => {
  await open(page)
  await page.evaluate(() => {
    const w = window as unknown as { __seen: number[] }
    w.__seen = []
    const tick = () => { w.__seen.push(window.__stage?.explode() ?? -1); requestAnimationFrame(tick) }
    tick()
  })
  await T(page, 'layer-row').first().click()
  await page.waitForFunction(() => (window.__stage?.explode() ?? 0) > 0.95, undefined, { timeout: 40000 })
  const values = await page.evaluate(() => (window as unknown as { __seen: number[] }).__seen)
  // a frame loop that renders fewer than a dozen frames while the ring opens (a machine under load) cannot show an in-between value: the check says so instead of guessing
  test.skip(values.length < 12, `only ${values.length} frames while the ring opened`)
  expect(values.some((v) => v > 0.05 && v < 0.95), `values seen: ${values.filter((_, i) => i % 15 === 0).map((v) => v.toFixed(2)).join(' ')}`).toBe(true)
})

test('inside-C15 the card enters with a fade and a rise, leaves with a fade, and a change swaps through the leave step', async ({ page }) => {
  await open(page)
  const id = linkedObject().id
  await page.goto(`/inside?part=${encodeURIComponent(id)}`)
  const enter = await css(page, '.in-pres', ['animation-name', 'animation-duration'])
  expect(enter['animation-name']).toBe('in-rise')
  expect(parseFloat(enter['animation-duration'] ?? '0')).toBeGreaterThan(0.2)
  // leaving: the phase goes to out (opacity 0 over a transition), then the card is gone
  await watchLeave(page)
  await T(page, 'card-close').click()
  await sawLeave(page)
  const out = await css(page, '.in-pres', ['transition-property'])
  expect(out['transition-property']).toContain('opacity')
  await expect(T(page, 'part-card')).toHaveCount(0)
  await expect(T(page, 'hint')).toBeVisible()
  // changing the part: the old card is still the one shown for the leave step, then the new one rises in
  const other = Object.keys(notes).find((k) => k.startsWith('ring:') && k !== id) ?? ''
  await page.goto(`/inside?part=${encodeURIComponent(id)}`)
  await expect(T(page, 'part-card')).toHaveAttribute('data-part-id', id)
  await watchLeave(page)
  await page.evaluate((o) => { history.pushState(null, '', `/inside?part=${encodeURIComponent(o)}`); dispatchEvent(new PopStateEvent('popstate')) }, other)
  await sawLeave(page)
  await expect(T(page, 'part-card')).toHaveAttribute('data-part-id', other)
})

test('inside-C16 search results fade in; the active layer carries an animated bar', async ({ page }) => {
  await open(page)
  await T(page, 'search').fill('a')
  const hits = await css(page, '[data-testid="inside.search-results"]', ['animation-name'])
  expect(hits['animation-name']).toBe('in-fade')
  const row = T(page, 'layer-row').nth(1)
  const idle = await css(page, '[data-testid="inside.layer-row"] >> nth=1', ['transform'], '::before')
  await row.click()
  await expect(row).toHaveAttribute('aria-pressed', 'true')
  const live = await css(page, '[data-testid="inside.layer-row"] >> nth=1', ['transition-duration', 'transform'], '::before')
  await expect.poll(async () => (await css(page, '[data-testid="inside.layer-row"] >> nth=1', ['transform'], '::before')).transform, { timeout: 8000 }).toBe('matrix(1, 0, 0, 1, 0, 0)')
  const done = await css(page, '[data-testid="inside.layer-row"] >> nth=1', ['transform'], '::before')
  expect(idle.transform).toBe('matrix(1, 0, 0, 0, 0, 0)')
  expect(parseFloat(live['transition-duration'] ?? '0')).toBeGreaterThan(0.2)
  expect(done.transform).toBe('matrix(1, 0, 0, 1, 0, 0)')
})

test('inside-C17 with reduced motion nothing animates: the card is there at once, no animation, no transition', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await open(page)
  await page.goto(`/inside?part=${encodeURIComponent(linkedObject().id)}`)
  await expect(T(page, 'part-card')).toBeVisible()
  const a = await css(page, '.in-pres', ['animation-duration'])
  expect(parseFloat(a['animation-duration'] ?? '1')).toBeLessThan(0.001)
  await T(page, 'card-close').click()
  await expect(T(page, 'part-card')).toHaveCount(0, { timeout: 400 })
  // choosing a part opened the ring at once (reduced motion): the control now offers to close it, and does so at once
  await expect(T(page, 'open-ring')).toHaveText('Close the ring', { timeout: 400 })
  await T(page, 'open-ring').click()
  await expect(T(page, 'open-ring')).toHaveText('Open the ring', { timeout: 400 })
})

test('inside-C18 same frame as Home: title, stamp line, section labels, banner type and list rows match by computed style', async ({ page }) => {
  await open(page)
  const props = ['font-size', 'font-family', 'font-weight', 'letter-spacing', 'color', 'text-transform']
  const inside = {
    title: await css(page, '[data-testid="inside.panel"] h1', props),
    stamp: await css(page, '[data-testid="inside.panel"] header .label', props),
    section: await css(page, '[data-testid="inside.panel"] .sec-title', props),
    gap: await css(page, '[data-testid="inside.panel"]', ['row-gap']),
    row: await css(page, '[data-testid="inside.layer-row"]', ['font-size', 'padding-top', 'padding-bottom']),
  }
  await page.goto('/')
  await expect(page.getByTestId('home.panel')).toBeVisible()
  const home = {
    title: await css(page, '[data-testid="home.panel"] h1', props),
    stamp: await css(page, '[data-testid="home.panel"] header .label', props),
    section: await css(page, '[data-testid="home.panel"] .sec-title', props),
    gap: await css(page, '[data-testid="home.panel"]', ['row-gap']),
    row: await css(page, '.kn-row, .next-link', ['font-size', 'padding-top', 'padding-bottom']),
  }
  expect(inside.title).toEqual(home.title)
  expect(inside.stamp).toEqual(home.stamp)
  expect(inside.section).toEqual(home.section)
  expect(inside.gap).toEqual(home.gap)
  expect(inside.row['padding-top']).toEqual(home.row['padding-top'])
  expect(inside.row['padding-bottom']).toEqual(home.row['padding-bottom'])
})

// ---- layout C: the ring above, the drawing below (inside-C19 .. C32) ----
type Line = { bom: string; item: string; maker: string | null; maker_part_number: string | null; open_action: string | null; part_ids: string[]; refs: string[]; size_mm: string | null }
const ringLines = (parts.lines as Line[]).filter((l) => l.bom === 'ring')
const madeLine = ringLines.find((l) => !l.maker && !l.maker_part_number && /\b(drawing|outline)\b/i.test(l.open_action ?? ''))
const boughtLine = ringLines.find((l) => l.maker && l.maker_part_number && notes[l.part_ids[0] ?? ''])
const MFG = 'design/mfg/'
const stageBox = (page: Page) => page.locator('[data-testid="inside.stage"]').boundingBox()
/** Adds made-up maker files for the made part to the files record (the real ones are made by another piece). */
const withMakerFiles = async (page: Page, ref: string) => {
  await page.route(/\/data\/files\.json/, async (r) => {
    const res = await r.fetch()
    const f = await res.json()
    f.files = f.files.filter((x: { path: string }) => !x.path.startsWith(MFG)) // only the made-up files below
    for (const n of ['size9.stl', 'size11.stl', 'size9.step', 'drawing.pdf', 'spec.pdf', 'front-size9.svg', 'front-size11.svg', 'top.svg'])
      f.files.push({ path: `${MFG}parts/${ref}-${n}`, size_bytes: 1, modified: '2026-11-10', area: 'inside', tracked: true })
    await r.fulfill({ response: res, json: f })
  })
}
const openPart = async (page: Page, id: string) => {
  await page.goto(`/inside?part=${encodeURIComponent(id)}`)
  await waitStageReady(page)
  await expect(T(page, 'part-card')).toBeVisible()
}

test('inside-C19 frame 1: one open button with its slider, the line on small parts with a link to Parts, a count, a link for the maker', async ({ page }) => {
  await open(page)
  await expect(T(page, 'open-ring')).toHaveCount(1)
  await expect(T(page, 'explode-slider')).toHaveAttribute('aria-label', 'Open it up')
  await expect(T(page, 'small-parts-note')).toContainText('not drawn in 3D')
  await expect(T(page, 'small-parts-note').locator('a')).toHaveAttribute('href', /\/parts$/)
  await expect(T(page, 'count')).toContainText(`${placements.placements.length} parts drawn in 3D, in ${placements.layers.length} layers`)
  await expect(T(page, 'link-for-manufacturer')).toHaveAttribute('href', /\/open#files$/)
  await expect(T(page, 'drawing-strip')).toHaveAttribute('data-open', 'false')
  await expect(T(page, 'selected-tag')).toHaveCount(0)
})

test('inside-C20 a made-to-drawing part: ring stays, strip slides up under it, the panel says Made to drawing and For the maker', async ({ page }) => {
  expect(madeLine, 'the bundle has a made-to-drawing part').toBeTruthy()
  const id = madeLine?.part_ids[0] ?? ''
  await open(page)
  const before = await stageBox(page)
  await openPart(page, id)
  await expect(T(page, 'drawing-strip')).toHaveAttribute('data-open', 'true')
  await expect(T(page, 'part-card')).toHaveAttribute('data-made', 'true')
  await expect(T(page, 'part-card')).toContainText('Made to drawing')
  await expect(T(page, 'part-card')).toContainText('For the maker')
  await expect(T(page, 'part-card').locator('h3')).toHaveText(madeLine?.item ?? '')
  await expect(T(page, 'file-button')).toHaveCount(4)
  await expect(T(page, 'links-out').locator('li')).toHaveCount(3)
  await expect(T(page, 'selected-tag')).toContainText(madeLine?.item ?? '')
  // the ring is above the strip: the stage's 3D box is shorter and ends where the strip starts
  await page.waitForTimeout(900)
  const after = await stageBox(page)
  const strip = await T(page, 'drawing-strip').boundingBox()
  expect((after?.height ?? 0)).toBeLessThan((before?.height ?? 0) * 0.8)
  expect((strip?.y ?? 0)).toBeGreaterThanOrEqual((after?.y ?? 0) + (after?.height ?? 0) - 2)
  expect(await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight)).toBe(true)
})

test('inside-C21 files not made yet are greyed with the contract wording, never a dead link; the strip says which views are not drawn', async ({ page }) => {
  await openPart(page, madeLine?.part_ids[0] ?? '')
  const files = json('files.json') as { files: { path: string; part_ids?: string[] }[] }
  const id = madeLine?.part_ids[0] ?? ''
  const made = files.files.filter((f) => f.path.startsWith(MFG) && (f.part_ids?.includes(id) || (madeLine?.refs ?? []).some((r) => f.path.toLowerCase().includes(r.toLowerCase()))))
  for (const b of await T(page, 'file-button').all()) {
    const href = await b.getAttribute('href')
    if (href) {
      const res = await page.request.get(href)
      expect(res.status(), `${href} answers`).toBe(200)
    } else {
      await expect(b).toHaveAttribute('aria-disabled', 'true')
      await expect(b).toContainText('not on disk')
    }
  }
  if (made.length === 0) {
    await expect(T(page, 'file-button').locator('em')).toHaveCount(4)
    await expect(T(page, 'strip-missing')).toContainText('front, side, top')
    await expect(T(page, 'drawing-view').and(page.locator('[data-drawn="no"]'))).toHaveCount(3)
    await expect(T(page, 'full-drawing')).toHaveAttribute('aria-disabled', 'true')
  }
  await expect(T(page, 'strip-sizes')).toContainText(madeLine?.size_mm ?? 'No main sizes')
})

test('inside-C22 files made for the part: four buttons link to them, the ring-size switch picks the size, the views are drawn', async ({ page }) => {
  const ref = madeLine?.refs[0] ?? ''
  await withMakerFiles(page, ref)
  await openPart(page, madeLine?.part_ids[0] ?? '')
  const kind = (k: string) => page.locator(`[data-testid="inside.file-button"][data-file="${k}"]`)
  await expect(T(page, 'size-switch').locator('button')).toHaveText(['9', '11'])
  await expect(kind('stl')).toHaveAttribute('href', new RegExp(`${ref}-size9\\.stl$`))
  await T(page, 'size-switch').locator('[data-size="11"]').click()
  await expect(kind('stl')).toHaveAttribute('href', new RegExp(`${ref}-size11\\.stl$`))
  await expect(kind('step')).toHaveAttribute('aria-disabled', 'true') // only size 9 has a STEP
  await expect(kind('drawing')).toHaveAttribute('href', /drawing\.pdf$/)
  await expect(kind('spec')).toHaveAttribute('href', /spec\.pdf$/)
  await expect(T(page, 'full-drawing')).toHaveAttribute('href', /drawing\.pdf$/)
  await expect(page.locator('[data-testid="inside.drawing-view"][data-view="front"] img')).toHaveAttribute('src', /front-size11\.svg$/)
  await expect(page.locator('[data-testid="inside.drawing-view"][data-view="top"] img')).toHaveAttribute('src', /top\.svg$/)
  await expect(T(page, 'strip-missing')).toContainText('side')
  await expect(T(page, 'strip-missing')).not.toContainText('front')
})

test('inside-C23 a bought part: no strip, maker, order code and datasheet in its card', async ({ page }) => {
  expect(boughtLine, 'the bundle has a bought part with a note').toBeTruthy()
  const id = boughtLine?.part_ids[0] ?? ''
  await openPart(page, id)
  await expect(T(page, 'drawing-strip')).toHaveAttribute('data-open', 'false')
  await expect(T(page, 'file-button')).toHaveCount(0)
  await expect(T(page, 'bought')).toContainText(boughtLine?.maker ?? '')
  await expect(T(page, 'bought')).toContainText(boughtLine?.maker_part_number ?? '')
  await expect(T(page, 'bought')).toContainText('Datasheet')
  await expect(T(page, 'part-card').first()).toContainText(notes[id]?.what ?? '')
  const box = await stageBox(page)
  expect(box?.height ?? 0).toBeGreaterThan(600 * 0.9)
})

test('inside-C24 All layers brings the list back, the strip slides down, the ring stays open', async ({ page }) => {
  await openPart(page, madeLine?.part_ids[0] ?? '')
  await page.waitForFunction(() => (window.__stage?.explode() ?? 0) > 0.95)
  await T(page, 'card-close').click()
  await expect(T(page, 'layers')).toBeVisible()
  await expect(T(page, 'drawing-strip')).toHaveAttribute('data-open', 'false')
  await expect(T(page, 'part-card')).toHaveCount(0)
  await page.waitForTimeout(2500) // long enough for a closing movement to show itself
  expect(await page.evaluate(() => window.__stage?.explode() ?? 0)).toBeGreaterThan(0.95)
  await expect(T(page, 'open-ring')).toHaveText('Close the ring')
})

test('inside-C25 the x on the tag and Escape both clear the selection', async ({ page }) => {
  const id = madeLine?.part_ids[0] ?? ''
  await openPart(page, id)
  await T(page, 'tag-clear').click()
  await expect(T(page, 'part-card')).toHaveCount(0)
  expect(new URL(page.url()).search).toBe('')
  await openPart(page, id)
  await page.keyboard.press('Escape')
  await expect(T(page, 'part-card')).toHaveCount(0)
  await expect(T(page, 'selected-tag')).toHaveCount(0)
})

test('inside-C26 a part chosen while the ring is closed opens the ring by easing', async ({ page }) => {
  await open(page)
  expect(await page.evaluate(() => window.__stage?.explode() ?? 0)).toBeLessThan(0.05)
  await page.evaluate((o) => { history.pushState(null, '', `/inside?part=${encodeURIComponent(o)}`); dispatchEvent(new PopStateEvent('popstate')) }, boughtLine?.part_ids[0] ?? '')
  await page.waitForFunction(() => (window.__stage?.explode() ?? 0) > 0.95, undefined, { timeout: 40000 })
})

test('inside-C27 the strip and the stage make room with eased transitions; reduced motion makes them instant', async ({ page }) => {
  await open(page)
  const strip = await css(page, '[data-testid="inside.drawing-strip"]', ['transition-property', 'transition-duration'])
  expect(strip['transition-property']).toContain('transform')
  expect(parseFloat(strip['transition-duration'] ?? '0')).toBeGreaterThan(0.2)
  const st = await css(page, '[data-testid="app.stage"]', ['transition-property'])
  expect(st['transition-property']).toContain('padding-bottom')
  await page.emulateMedia({ reducedMotion: 'reduce' })
  const quick = await css(page, '[data-testid="inside.drawing-strip"]', ['transition-duration'])
  expect(parseFloat(quick['transition-duration'] ?? '1')).toBeLessThan(0.001)
})

test('inside-C28 the panel holds the part card without sideways scroll at 1280 x 800 and 1440 x 900', async ({ page }) => {
  for (const [w, h] of [[1280, 800], [1440, 900]] as const) {
    await page.setViewportSize({ width: w, height: h })
    await openPart(page, madeLine?.part_ids[0] ?? '')
    await page.waitForTimeout(700)
    const m = await page.evaluate(() => ({ sh: document.documentElement.scrollHeight, ih: innerHeight, sw: document.documentElement.scrollWidth, iw: innerWidth }))
    expect(m.sh, `${w}`).toBeLessThanOrEqual(m.ih)
    expect(m.sw, `${w}`).toBeLessThanOrEqual(m.iw)
    const p = await page.getByTestId('app.panel-body').evaluate((e) => ({ sw: e.scrollWidth, cw: e.clientWidth }))
    expect(p.sw).toBeLessThanOrEqual(p.cw)
    const strip = await T(page, 'drawing-strip').evaluate((e) => ({ sw: e.scrollWidth, cw: e.clientWidth, sh: e.scrollHeight, ch: e.clientHeight }))
    expect(strip.sw).toBeLessThanOrEqual(strip.cw)
    expect(strip.sh).toBeLessThanOrEqual(strip.ch)
  }
})

test('inside-C29 links out of a made part: Source opens in a new tab, Parts line and Maker files go to their screens', async ({ page }) => {
  await openPart(page, madeLine?.part_ids[0] ?? '')
  const id = madeLine?.part_ids[0] ?? ''
  const src = T(page, 'link-source')
  if (await src.count()) await expect(src).toHaveAttribute('target', '_blank')
  await expect(T(page, 'link-parts-line')).toHaveAttribute('href', new RegExp(`/parts\\?part=${encodeURIComponent(id).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`))
  await expect(T(page, 'link-maker-files')).toHaveAttribute('href', /\/open#files$/)
})

test('inside-C30 a layer opened to its part names still selects a part, and a made part there opens the strip', async ({ page }) => {
  const id = madeLine?.part_ids[0] ?? ''
  const obj = placements.placements.find((p) => Object.keys(notes).some((k) => k === id && notes[k]?.model_names.includes(p.name)))
  test.skip(!obj, 'the made part has no object in the model')
  await open(page)
  await page.locator(`[data-testid="inside.layer-row"][data-layer="${obj?.layer}"]`).click()
  await page.locator(`[data-testid="inside.layer-part"][data-object="${obj?.name}"]`).click()
  await expect(T(page, 'drawing-strip')).toHaveAttribute('data-open', 'true')
})

test('inside-C31 empty bundle: the open control is off, the strip stays shut, no script error', async ({ page }) => {
  const w = watchConsole(page)
  await page.route(/\/(data\/[^?]*\.(json|glb|zip)|content\/part-notes\.json)(\?.*)?$/, (r) => r.fulfill({ status: 404, contentType: 'application/json', body: '{}' }))
  await page.goto('/inside')
  await expect(T(page, 'state-banner').first()).toContainText('Not built yet.')
  await expect(T(page, 'open-ring')).toBeDisabled()
  await expect(T(page, 'drawing-strip')).toHaveAttribute('data-open', 'false')
  await expect(T(page, 'count')).toHaveCount(0)
  expect(w.errors.filter((e) => !resourceNoise(e))).toEqual([])
})

test('inside-C32 an object with no parts-list line opens no strip and says so', async ({ page }) => {
  await open(page, '?object=made_up_object_name')
  await expect(T(page, 'part-card-no-line')).toHaveText('no parts-list line for this object')
  await expect(T(page, 'drawing-strip')).toHaveAttribute('data-open', 'false')
})

test('inside-C33 one opening value, two controls: the slider scrubs the ring, the button animation moves the slider', async ({ page }) => {
  await open(page)
  const slider = T(page, 'explode-slider')
  await slider.fill('0.6')
  await page.waitForFunction(() => Math.abs((window.__stage?.explode() ?? 0) - 0.6) < 0.05, undefined, { timeout: 30000 })
  await expect(T(page, 'open-ring')).toHaveText('Close the ring') // past halfway counts as open
  await T(page, 'open-ring').click()
  await expect.poll(async () => Number(await slider.inputValue()), { timeout: 20000 }).toBeLessThan(0.02)
  await page.waitForFunction(() => (window.__stage?.explode() ?? 1) < 0.05, undefined, { timeout: 30000 })
  await T(page, 'open-ring').click()
  await expect.poll(async () => Number(await slider.inputValue()), { timeout: 20000 }).toBe(1)
  await page.waitForFunction(() => (window.__stage?.explode() ?? 0) > 0.99, undefined, { timeout: 30000 })
})

test('inside-C35 the word beside the slider follows the value: Closed at 0, a percentage between, Open at 1', async ({ page }) => {
  await open(page)
  const w = T(page, 'explode-closed')
  await expect(w).toHaveText('Closed')
  await T(page, 'explode-slider').fill('0.6')
  await expect(w).toHaveText('60%')
  await T(page, 'explode-slider').fill('1')
  await expect(w).toHaveText('Open')
  await T(page, 'explode-slider').fill('0')
  await expect(w).toHaveText('Closed')
})

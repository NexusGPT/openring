// J2: Compare the exterior options (docs/JOURNEYS.md J2.1 to J2.3; rows J2#1 to J2#3 of docs/TEST-PLAN.md section 3),
// plus J2#4 for the screen states (not a journey step: the owner's Look switches). Written from the journey table.
// Every expected value is read from the bundle (looks/index.json, ring-model.json) or the contract's words; none is typed here.
// The journey names options A, B, C of an earlier design; today the screen shows the record's open options
// (rejected ones never), so "the options" below are the record's non-rejected options (the picked one alone when set).
// Ids on the page: look.finish / look.screen / look.view (buttons, data-value, aria-pressed), look.<name>-switch,
// look.<name>-more, look.look-option (data-option), app.stage with window.__stage, home.area-tile.
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect as baseExpect, test, type Locator, type Page } from '@playwright/test'
import { banner } from '../src/contract/vocabulary'
import { FIXTURE_DATA, blockOffline, byTestId, watchConsole } from '../tests/support'

const expect = baseExpect.configure({ timeout: 15_000 })
test.describe.configure({ timeout: 90_000 })

const J2_1 = "J2#1"
const J2_2 = "J2#2"
const J2_3 = "J2#3"
const J2_4 = "J2#4"

const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
function bundleRecord<T>(file: string): T {
  if (!existsSync(join(BUNDLE, 'manifest.json'))) throw new Error(`journey setup: no bundle at ${BUNDLE}; set EXPLORER_BUNDLE`)
  const p = join(BUNDLE, file)
  if (!existsSync(p)) throw new Error(`journey setup: record ${file} is missing from the bundle ${BUNDLE}`)
  return JSON.parse(readFileSync(p, 'utf8')) as T
}
interface Option { id: string; title: string; sentence: string | null; worse_at: string[]; rejected: boolean; in_design: boolean; source: { file: string; line: number | null }; glb: { bounds_mm: { x: number; y: number; z: number } } | null }
interface Looks { finishes: { name: string; colour: string }[]; options: Option[]; picked?: string | null }
interface Ring { exterior: { status: string }; screens: { states: { state: string; label?: string; fields: { label?: string | null }[] }[] } }
const looks = () => bundleRecord<Looks>('looks/index.json')
const ring = () => bundleRecord<Ring>('ring-model.json')
/** The options the screen must show: not rejected; once one is picked, that one alone. */
const shown = (): Option[] => {
  const l = looks()
  const open = l.options.filter((o) => !o.rejected)
  return l.picked ? open.filter((o) => o.id === l.picked) : open
}

const norm = (s: string) => s.replace(/\s+/g, ' ').trim()
const canvas = (page: Page): Locator => byTestId(page, 'app', 'stage').locator('canvas')
const angleDiff = (a: number, b: number) => Math.abs(((((a - b) % 360) + 540) % 360) - 180)

async function pixels(page: Page, a: Buffer, b: Buffer): Promise<number> {
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
      const B = await load(bb)
      let n = 0
      const total = A.width * A.height
      for (let i = 0; i < total; i++) {
        const o = i * 4
        if (Math.abs(A.data[o]! - B.data[o]!) > 12 || Math.abs(A.data[o + 1]! - B.data[o + 1]!) > 12 || Math.abs(A.data[o + 2]! - B.data[o + 2]!) > 12) n++
      }
      return n / total
    },
    [a.toString('base64'), b.toString('base64')] as [string, string],
  )
}
async function stageReady(page: Page): Promise<void> {
  await expect.poll(() => page.evaluate(() => window.__stage?.ready === true), { timeout: 25_000, message: 'the 3D stage never reported ready' }).toBe(true)
}
/** Home, tile Look; the screen's first assertion is the switches panel so a missing screen fails by name. */
async function openLook(page: Page): Promise<void> {
  const w = watchConsole(page)
  await blockOffline(page, w)
  await page.goto('/')
  const tile = byTestId(page, 'home', 'area-tile').and(page.locator('[data-area="look"]'))
  await expect(tile, 'Home has no Look tile').toBeVisible({ timeout: 20_000 })
  await tile.click()
  await expect(page, 'the Look tile did not go to /look').toHaveURL(/\/look(\/|\?|#|$)/)
  await expect(byTestId(page, 'look', 'switches'), 'Look has no switches (look.switches)').toBeVisible()
  await stageReady(page)
}
/** Stop the stage's own turning (the first drag does it) and let it settle, so a picture difference is the user's change. */
async function stillStage(page: Page): Promise<void> {
  const box = (await canvas(page).boundingBox())!
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await page.mouse.down()
  await page.mouse.move(box.x + box.width / 2 + 60, box.y + box.height / 2, { steps: 6 })
  await page.mouse.up()
  expect(await page.evaluate(() => window.__stage!.autoRotate), 'auto-rotate must stop after the first drag').toBe(false)
  await page.mouse.move(2, 2)
  let last = await page.evaluate(() => window.__stage!.azimuthDeg())
  for (let i = 0; i < 20; i++) {
    await page.waitForTimeout(500)
    const now = await page.evaluate(() => window.__stage!.azimuthDeg())
    if (angleDiff(now, last) < 0.05) return
    last = now
  }
}
const btn = (page: Page, name: 'finish' | 'screen' | 'view', value: string): Locator => byTestId(page, 'look', name).and(page.locator(`[data-value="${value}"]`))
async function pick(page: Page, name: 'finish' | 'screen' | 'view', value: string): Promise<void> {
  let b = btn(page, name, value)
  if ((await b.count()) === 0) {
    const more = byTestId(page, 'look', `${name}-more`)
    if ((await more.count()) > 0) await more.click()
    b = btn(page, name, value)
  }
  await expect(b, `no ${name} button '${value}' (look.${name}[data-value])`).toBeVisible()
  await b.click()
  await expect(b).toHaveAttribute('aria-pressed', 'true')
  await page.mouse.move(2, 2)
  await page.waitForTimeout(1_200) // the stage eases the change
}
const shot = (page: Page) => canvas(page).screenshot()

// ---- J2.1 --------------------------------------------------------------------------------------------
test(`${J2_1} (J2.1) Look: the exterior and its words come from the record, and the ring turns by hand`, async ({ page }) => {
  await openLook(page)

  // the exterior state sentence of the contract, from the ring-model status
  const status = ring().exterior.status
  const spec = status === 'in-design' ? ({ kind: 'exterior-in-design' } as const) : status === 'not-picked' ? ({ kind: 'exterior-not-picked' } as const) : null
  const panel = byTestId(page, 'app', 'panel')
  if (spec) await expect(panel, `the exterior is '${status}' but the panel does not say so`).toContainText(banner(spec).sentence)
  else await expect(panel.getByText(/Exterior (in design|not picked)/)).toHaveCount(0)

  // one panel per shown option, with title, sentence and trade-offs equal to the record's
  const opts = shown()
  expect(opts.length, 'control: the record has no option to show').toBeGreaterThan(0)
  const panels = byTestId(page, 'look', 'look-option')
  await expect(panels).toHaveCount(opts.length)
  for (const o of opts) {
    const p = panels.and(page.locator(`[data-option="${o.id}"]`))
    await expect(p, `no panel for option '${o.id}'`).toHaveCount(1)
    await expect(p.locator('.opt-title, h3').first()).toHaveText(o.title)
    if (o.sentence) await expect(p).toContainText(o.sentence)
    const worse = await p.locator('li').allInnerTexts()
    expect(worse.map(norm), `trade-offs of '${o.id}' differ from the record`).toEqual(o.worse_at.map(norm))
    await p.locator('summary').click()
    await expect(p, `details of '${o.id}' lack the source`).toContainText(`${o.source.file}${o.source.line ? `:${o.source.line}` : ''}`)
    if (o.glb) await expect(p, `details of '${o.id}' lack the bounds`).toContainText(String(o.glb.bounds_mm.x))
  }
  // a rejected option never appears
  for (const o of looks().options.filter((x) => x.rejected)) await expect(panels.and(page.locator(`[data-option="${o.id}"]`))).toHaveCount(0)

  // rotates one: the 200 px drag turns the ring over 20 degrees
  const box = (await canvas(page).boundingBox())!
  const az0 = await page.evaluate(() => window.__stage!.azimuthDeg())
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await page.mouse.down()
  await page.mouse.move(box.x + box.width / 2 + 200, box.y + box.height / 2, { steps: 12 })
  await page.mouse.up()
  expect(angleDiff(await page.evaluate(() => window.__stage!.azimuthDeg()), az0), 'the drag did not turn the ring by over 20 degrees').toBeGreaterThan(20)
  if (opts.length < 2) test.info().annotations.push({ type: 'not-exercised', description: 'one option shown: "all rotate together or one alone" cannot be seen' })
})

// ---- J2.2 --------------------------------------------------------------------------------------------
test(`${J2_2} (J2.2) Look: each finish changes the ring`, async ({ page }) => {
  await openLook(page)
  const finishes = looks().finishes
  expect(finishes.length, 'control: the record has fewer than 2 finishes').toBeGreaterThan(1)
  await expect(byTestId(page, 'look', 'finish'), 'the finish switch lists a different count than the record').toHaveCount(finishes.length)
  await stillStage(page)

  // control for the picture probe: with nothing changed two pictures are the same
  const a0 = await shot(page)
  await page.waitForTimeout(600)
  expect(await pixels(page, a0, await shot(page)), 'control: the picture changes with no input; the probe is not stable').toBeLessThan(0.002)

  let prev = await shot(page)
  for (const f of finishes) {
    const b = btn(page, 'finish', f.name)
    await expect(b, `no finish button '${f.name}'`).toBeVisible()
    if ((await b.getAttribute('aria-pressed')) === 'true') continue // already on: the next finish is compared with it
    await pick(page, 'finish', f.name)
    const now = await shot(page)
    expect(await pixels(page, prev, now), `finish '${f.name}' did not change the ring picture`).toBeGreaterThanOrEqual(0.005)
    prev = now
  }
  // the swatch of each button is the record's colour
  for (const f of finishes) {
    const dot = btn(page, 'finish', f.name).locator('.sw-dot')
    const bg = await dot.evaluate((e) => getComputedStyle(e).backgroundColor)
    const hex = f.colour.replace('#', '')
    const want = `rgb(${parseInt(hex.slice(0, 2), 16)}, ${parseInt(hex.slice(2, 4), 16)}, ${parseInt(hex.slice(4, 6), 16)})`
    expect(bg, `swatch of '${f.name}'`).toBe(want)
  }
})

// ---- J2.3 --------------------------------------------------------------------------------------------
test(`${J2_3} (J2.3) Look: each view moves the camera and "on a finger" puts the ring on a finger`, async ({ page }) => {
  await openLook(page)
  const views = ['three-quarter', 'top', 'side', 'finger']
  await expect(byTestId(page, 'look', 'view')).toHaveCount(views.length)
  const ids = shown().map((o) => o.id)
  const fingerOf = (page2: Page) => page2.evaluate((cands) => cands.map((c) => window.__stage!.fingerVisible(c)), [...ids, 'exterior'])
  await stillStage(page)
  const pictures: Buffer[] = []
  for (const v of views) {
    await pick(page, 'view', v)
    expect(await page.evaluate(() => window.__stage!.preset()), `stage preset after choosing '${v}'`).toBe(v)
    const onFinger = (await fingerOf(page)).some(Boolean)
    expect(onFinger, v === 'finger' ? 'on a finger: no finger cylinder is shown' : `view '${v}' shows a finger`).toBe(v === 'finger')
    pictures.push(await shot(page))
  }
  for (let i = 1; i < pictures.length; i++) expect(await pixels(page, pictures[i - 1]!, pictures[i]!), `view '${views[i]}' looks the same as '${views[i - 1]}'`).toBeGreaterThanOrEqual(0.01)
})

// ---- J2.4 (screen states) ----------------------------------------------------------------------------
test(`${J2_4} (J2.4) Look: each screen state draws the fields of the record, and Off draws none`, async ({ page }) => {
  await openLook(page)
  const states = ring().screens.states
  expect(states.length, 'control: the record has no screen state').toBeGreaterThan(0)
  for (const s of states) {
    await pick(page, 'screen', s.state)
    const want = s.fields.flatMap((f) => (f.label ? [f.label] : []))
    expect(want.length, `control: state '${s.state}' lists no field label`).toBeGreaterThan(0)
    expect(await page.evaluate(() => window.__stage!.screenFields()), `screen fields of state '${s.state}'`).toEqual(want)
  }
  await pick(page, 'screen', 'off')
  expect(await page.evaluate(() => window.__stage!.screenFields()), 'Off must draw no field').toEqual([])
})

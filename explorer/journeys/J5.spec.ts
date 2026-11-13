// J5: See how the ring behaves (docs/JOURNEYS.md J5.1 to J5.3; rows J5#1 to J5#3 of docs/TEST-PLAN.md section 3).
// Written from the signed journey table, never from a built screen. Every expected value (rest state, hold time,
// recording state, motor pulses, effects per state) is read from the bundle's behaviour.json at run time (EXPLORER_BUNDLE).
// Entry: Home, tile "Behaviour". The press is a real mouse down, wait, mouse up on the button's centre. Headless only.
// Ids on the page: behaviour.{panel,state,light,timer,highlights,highlight-mark,vibration,vibration-mark,joystick-centre,
// joystick,joystick-button,state-list,state-item,hold-progress}; `data-stage-elapsed` on behaviour.panel.
// Red-first switches (never set in a normal run): J5_HOLD_MS (the length of the long holds), J5_HOLD2_MS (the second
// hold of J5.3), J5_TAP_MS (the tap in J5.2).
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect as baseExpect, test, type Locator, type Page } from '@playwright/test'
import { FIXTURE_DATA, blockOffline, byTestId, watchConsole } from '../tests/support'

const expect = baseExpect.configure({ timeout: 8_000 })
test.describe.configure({ timeout: 90_000 })

const J5_1 = 'J5#1'
const J5_2 = 'J5#2'
const J5_3 = 'J5#3'

const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
function bundleRecord<T>(file: string): T {
  if (!existsSync(join(BUNDLE, 'manifest.json'))) throw new Error(`journey setup: no bundle at ${BUNDLE} (manifest.json missing); set EXPLORER_BUNDLE`)
  const p = join(BUNDLE, file)
  if (!existsSync(p)) throw new Error(`journey setup: record ${file} is missing from the bundle ${BUNDLE}`)
  return JSON.parse(readFileSync(p, 'utf8')) as T
}

interface Gesture { kind: string; min_hold_ms: number | null; max_hold_ms: number | null; window_ms: number | null; per_state: { state: string; effect: string }[] }
interface StateRec { id: string; label: string; meaning: string; microphones: string; screen: string }
interface Transition { from: string; to: string; event_kind: string; motor_ids: string[] }
interface Pattern { id: string; event: string; pulses: { on_ms: number; off_ms: number }[] }
interface Rules {
  gestures: Gesture[]
  joystick: { direction: string; effect: string }[]
  light_rule: { on_where_microphones_on: boolean }
  states: StateRec[]
  transitions: Transition[]
  motor_patterns: Pattern[]
}
const RULES = (): Rules => bundleRecord<Rules>('behaviour.json')
const gesture = (r: Rules, kind: string): Gesture => {
  const g = r.gestures.find((x) => x.kind === kind)
  if (!g) throw new Error(`journey setup: behaviour.json has no gesture '${kind}'`)
  return g
}
const stateOf = (r: Rules, id: string): StateRec => {
  const s = r.states.find((x) => x.id === id)
  if (!s) throw new Error(`journey setup: behaviour.json has no state '${id}'`)
  return s
}
/** The state a long press leaves for a state with the microphones on, and a long press leaves back: the ring's rest state. */
function restAndRecording(r: Rules): { rest: string; rec: string } {
  const longs = r.transitions.filter((t) => t.event_kind === 'long_press' && t.from !== t.to)
  for (const t of longs) {
    if (stateOf(r, t.to).microphones === 'on' && longs.some((u) => u.from === t.to && u.to === t.from)) return { rest: t.from, rec: t.to }
  }
  throw new Error('journey setup: behaviour.json has no pair of long-press transitions between a resting state and a microphone state')
}
const transition = (r: Rules, from: string, kind: string): Transition => {
  const t = r.transitions.find((x) => x.from === from && x.event_kind === kind)
  if (!t) throw new Error(`journey setup: no '${kind}' transition from ${from} in behaviour.json`)
  return t
}
/** The 'on' lengths of the vibration marks a list of motor patterns draws, in order. */
const marksOf = (r: Rules, ids: string[]): number[] =>
  ids.flatMap((id) => {
    const p = r.motor_patterns.find((x) => x.id === id)
    if (!p) throw new Error(`journey setup: no motor pattern ${id}`)
    return p.pulses.map((q) => q.on_ms)
  })

// ---- page helpers ------------------------------------------------------------------------------------
const tile = (page: Page, area: string): Locator => byTestId(page, 'home', 'area-tile').and(page.locator(`[data-area="${area}"]`))
const stateEl = (page: Page) => byTestId(page, 'behaviour', 'state')
const lightEl = (page: Page) => byTestId(page, 'behaviour', 'light')
const timerEl = (page: Page) => byTestId(page, 'behaviour', 'timer')
const button = (page: Page) => byTestId(page, 'behaviour', 'joystick-centre')
const marks = (page: Page) => byTestId(page, 'behaviour', 'vibration-mark')
const highlights = (page: Page) => byTestId(page, 'behaviour', 'highlights')

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
async function toBehaviour(page: Page): Promise<void> {
  await page.goto('/')
  const t = tile(page, 'behaviour')
  await expect(t, 'Home has no Behaviour tile (home.area-tile[data-area=behaviour])').toBeVisible()
  await t.click()
  await expect(page, 'the tile "Behaviour" did not go to /behaviour').toHaveURL(/\/behaviour(\/|\?|#|$)/)
  await expect(byTestId(page, 'behaviour', 'panel'), 'no Behaviour panel (behaviour.panel)').toBeVisible()
  await stageReady(page)
}
/** A real press: mouse down on the centre of the button, wait, mouse up. */
async function hold(page: Page, ms: number): Promise<void> {
  const b = button(page)
  await expect(b, 'no centre press on the joystick (behaviour.joystick-centre)').toBeVisible()
  const box = await b.boundingBox()
  if (!box) throw new Error('the joystick centre has no box')
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await page.mouse.down()
  await page.waitForTimeout(ms)
  await page.mouse.up()
}
const seconds = (t: string): number => {
  const m = /^(\d+):(\d{2}):(\d{2})$/.exec(t.trim())
  if (!m) throw new Error(`the timer reads '${t}', not hh:mm:ss`)
  return Number(m[1]) * 3600 + Number(m[2]) * 60 + Number(m[3])
}
/** Panel timer text and the panel's data-stage-elapsed, read in one browser turn. */
const clockNow = (page: Page) =>
  page.evaluate(() => {
    const t = document.querySelector('[data-testid="behaviour.timer"]')?.textContent ?? ''
    const e = document.querySelector('[data-testid="behaviour.panel"]')?.getAttribute('data-stage-elapsed') ?? null
    return { t, e }
  })
const snapshot = async (page: Page) => ({
  state: await stateEl(page).getAttribute('data-state-id'),
  light: await lightEl(page).getAttribute('data-on'),
  timer: (await timerEl(page).textContent())?.trim(),
  highlights: await highlights(page).getAttribute('data-count'),
  marks: await marks(page).count(),
})
async function expectState(page: Page, r: Rules, id: string, why: string): Promise<void> {
  await expect(stateEl(page), `${why}: the state is not '${id}'`).toHaveAttribute('data-state-id', id)
  await expect(stateEl(page), `${why}: the state name is not the record's label for ${id}`).toHaveText(stateOf(r, id).label)
  const lightOn = r.light_rule.on_where_microphones_on && stateOf(r, id).microphones === 'on'
  await expect(lightEl(page), `${why}: the light is ${lightOn ? 'not on' : 'on'} in ${id}`).toHaveAttribute('data-on', String(lightOn))
  await expect.poll(() => page.evaluate(() => window.__stage?.lightOn()), { message: `${why}: the 3D ring's light disagrees with the record in ${id}` }).toBe(lightOn)
}
/** "What a press does now": the rows listed equal the record's gesture effects for the state. */
async function expectDoesNow(page: Page, r: Rules, id: string): Promise<void> {
  const section = page.getByRole('heading', { name: 'What a press does now' }).locator('xpath=..')
  const want = r.gestures.flatMap((g) => g.per_state.filter((p) => p.state === id).map((p) => ({ kind: g.kind.replace(/_/g, ' '), effect: p.effect })))
  expect(want.length, `control: the record lists no press effect for ${id}`).toBeGreaterThan(0)
  const rows = section.locator('li')
  await expect(rows, `"What a press does now" lists a different number of rows than the record's effects for ${id}`).toHaveCount(Math.min(want.length, 4))
  for (let i = 0; i < Math.min(want.length, 4); i++) {
    await expect(rows.nth(i).locator('.does-kind'), `row ${i} names the wrong gesture`).toHaveText(want[i]!.kind)
    await expect(rows.nth(i).locator('.does-effect'), `row ${i} (${want[i]!.kind}) says something other than the record: ${want[i]!.effect}`).toHaveText(want[i]!.effect)
  }
  // consistency with the record's transitions: a gesture is listed exactly when a transition from this state is fired by it
  const fired = new Set(r.transitions.filter((t) => t.from === id && ['long_press', 'short_press', 'double_press'].includes(t.event_kind)).map((t) => t.event_kind))
  const listed = new Set(want.map((w) => w.kind.replace(/ /g, '_')))
  expect([...listed].sort(), `the record's gesture effects and its transitions disagree about what a press does in ${id}`).toEqual([...fired].sort())
}
/** The joystick: four directions and the centre press. Each direction does what the record lists for the state. */
async function expectJoystick(page: Page, r: Rules, id: string): Promise<void> {
  const btns = byTestId(page, 'behaviour', 'joystick-button')
  expect(r.joystick.length, 'control: the record lists no joystick control').toBe(5)
  const centre = await page.locator('.joy-centre').getAttribute('data-direction')
  const centreRule = r.joystick.find((j) => j.direction === centre)
  expect(centreRule, `the centre of the pad names '${centre}', which the record does not list`).toBeTruthy()
  await expect(button(page), 'the tooltip of the centre press is not the record\'s effect text').toHaveAttribute('title', centreRule!.effect)
  await expect(btns, 'the joystick pad does not show the four directions of the record').toHaveCount(r.joystick.length - 1)
  for (const j of r.joystick.filter((x) => x.direction !== centre)) {
    const b = btns.and(page.locator(`[data-direction="${j.direction}"]`))
    await expect(b, `no pad control for '${j.direction}'`).toHaveCount(1)
    await expect(b, `the tooltip of '${j.direction}' is not the record's effect text`).toHaveAttribute('title', j.effect)
    const t = r.transitions.find((x) => x.from === id && x.event_kind === 'joystick')
    const before = await snapshot(page)
    await b.click()
    if (t) {
      await expectState(page, r, t.to, `joystick '${j.direction}'`)
      expect(await marks(page).count(), `joystick '${j.direction}' drew another number of vibration marks than its motor patterns`).toBe(before.marks + marksOf(r, t.motor_ids).length)
    } else {
      await page.waitForTimeout(250)
      const after = await snapshot(page)
      expect(after.state, `joystick '${j.direction}' changed the state though the record has no joystick transition from ${id}`).toBe(before.state)
      expect(after.light, `joystick '${j.direction}' changed the light`).toBe(before.light)
      expect(after.highlights, `joystick '${j.direction}' added a highlight`).toBe(before.highlights)
      // the only vibration the record ties to the joystick is the pattern whose event names it (MT today), "only when screen
      // is on". The screen's on/off is not modelled by the app, so a press draws that pattern or nothing: never another count.
      const tick = marksOf(r, r.motor_patterns.filter((p) => /joystick/i.test(p.event)).map((p) => p.id))
      expect(tick.length, 'control: the record lists no joystick vibration pattern').toBeGreaterThan(0)
      expect([0, tick.length], `joystick '${j.direction}' drew ${after.marks - before.marks} vibration marks; the record's joystick pattern has ${tick.length}`).toContain(after.marks - before.marks)
    }
  }
}
const HOLD_MS = (r: Rules): number => Number(process.env.J5_HOLD_MS ?? gesture(r, 'long_press').min_hold_ms! + 150)
/** Hold to start a recording, from the rest state; waits for the recording state. */
async function startRecording(page: Page, r: Rules, rec: string): Promise<void> {
  await hold(page, HOLD_MS(r))
  await expectState(page, r, rec, 'setup: the long hold')
}

test(`${J5_1} (J5.1) Behaviour: standby shows the rest state; short presses change nothing; a long hold starts the recording, light, timer and vibration`, async ({ page }) => {
  const w = await boot(page)
  const r = RULES()
  const { rest, rec } = restAndRecording(r)
  const long = gesture(r, 'long_press')
  const short = gesture(r, 'short_press')
  expect(long.min_hold_ms, 'control: no long-press time in behaviour.json').toBeGreaterThan(0)
  expect(short.max_hold_ms!, 'control: the short press must be shorter than the long press').toBeLessThan(long.min_hold_ms!)
  await toBehaviour(page)

  // sees: the rest state, light off, no timer, no marks
  await expectState(page, r, rest, 'on arrival')
  await expect(timerEl(page), 'a timer runs while the ring is at rest').toHaveText('—')
  await expect(marks(page), 'vibration marks before any press').toHaveCount(0)
  await expect(highlights(page)).toHaveAttribute('data-count', '0')
  await expectDoesNow(page, r, rest)
  await expectJoystick(page, r, rest)
  const base = await marks(page).count()
  await expect(byTestId(page, 'behaviour', 'state-item').and(page.locator(`[data-state-id="${rest}"]`)), 'the state list does not mark the rest state as current').toHaveAttribute('data-current', 'true')
  await expect(byTestId(page, 'behaviour', 'state-item')).toHaveCount(r.states.length)

  // presses shorter than the long-press time change nothing that records: a tap, and a near miss just under the long time
  const near = long.min_hold_ms! - 300
  for (const ms of [short.min_hold_ms! + 160, near]) {
    await hold(page, ms)
    await page.waitForTimeout(short.window_ms! + 300)
    await expectState(page, r, rest, `a press of ${ms} ms (long press needs ${long.min_hold_ms} ms)`)
    await expect(timerEl(page), `a press of ${ms} ms started a timer`).toHaveText('—')
    await expect(highlights(page), `a press of ${ms} ms in ${rest} added a highlight`).toHaveAttribute('data-count', '0')
  }
  await expect(marks(page), 'a short press made the ring vibrate while at rest').toHaveCount(base)

  // does: holds the button for the long-press time (+150 ms)
  await hold(page, HOLD_MS(r))
  await expectState(page, r, rec, 'after the long hold')

  // visible result: one vibration mark per the start pattern, timer counts, 3D ring gets the same elapsed seconds as the panel
  const startMarks = marksOf(r, transition(r, rest, 'long_press').motor_ids)
  await expect(marks(page), 'vibration marks after the start differ from the start pattern of the record').toHaveCount(base + startMarks.length)
  expect((await marks(page).evaluateAll((els) => els.map((e) => Number(e.getAttribute('data-on-ms'))))).slice(-startMarks.length), 'vibration mark lengths differ from the record').toEqual(startMarks)
  const t0 = seconds((await timerEl(page).textContent())!)
  await page.waitForTimeout(1300)
  const c1 = await clockNow(page)
  expect(seconds(c1.t), `the timer did not count: ${t0} s then ${c1.t}`).toBeGreaterThan(t0)
  expect(c1.e, 'the panel passes no elapsed seconds to the 3D ring (data-stage-elapsed)').toBe(String(seconds(c1.t)))
  await page.waitForTimeout(1100)
  const c2 = await clockNow(page)
  expect(Number(c2.e), 'the elapsed seconds on the panel stopped counting').toBeGreaterThan(Number(c1.e))
  // the ring's screen shows the recording state's fields (the screen whose label names the state)
  const ring = bundleRecord<{ screens: { states: { state: string; label: string; fields: { kind: string; label: string | null }[] }[] } }>('ring-model.json')
  const face = ring.screens.states.find((s) => new RegExp(`(^|[^A-Za-z0-9_])${rec}([^A-Za-z0-9_]|$)`).test(s.label))
  expect(face, `control: no screen state of the ring is labelled with ${rec}`).toBeTruthy()
  expect(face!.fields.some((f) => f.kind === 'timer'), 'control: the recording screen has no timer field').toBe(true)
  expect(await page.evaluate(() => window.__stage!.screenFields()), 'the ring screen does not show the recording screen of the record').toEqual(face!.fields.map((f) => f.label).filter((l): l is string => !!l))
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

test(`${J5_2} (J5.2) Behaviour: in the recording state one tap adds exactly one highlight; the recording continues`, async ({ page }) => {
  const w = await boot(page)
  const r = RULES()
  const { rec } = restAndRecording(r)
  const short = gesture(r, 'short_press')
  await toBehaviour(page)
  await startRecording(page, r, rec)
  await expectDoesNow(page, r, rec)
  const before = await snapshot(page)
  expect(before.highlights, 'control: highlights are not 0 before the tap').toBe('0')
  const t0 = seconds(before.timer!)

  // does: taps once
  const tap = Number(process.env.J5_TAP_MS ?? short.min_hold_ms! + 160)
  await hold(page, tap)
  await page.waitForTimeout(short.window_ms! + 400)
  const hl = transition(r, rec, 'short_press')
  await expect(highlights(page), 'one tap did not add exactly one highlight').toHaveAttribute('data-count', '1')
  await expect(byTestId(page, 'behaviour', 'highlight-mark'), 'the highlight mark is not drawn').toHaveCount(1)
  await expect(marks(page), 'the highlight vibration is not drawn').toHaveCount(before.marks + marksOf(r, hl.motor_ids).length)
  // the recording continues: same state, light on, timer still counting
  await expectState(page, r, rec, 'after the tap')
  await page.waitForTimeout(1300)
  expect(seconds((await timerEl(page).textContent())!), 'the timer stopped after the tap').toBeGreaterThan(t0)
  await expect(highlights(page), 'the highlight count changed without a press').toHaveAttribute('data-count', '1')

  // the joystick pad in the recording state: each control does what the record lists for this state
  await expectJoystick(page, r, rec)
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

test(`${J5_3} (J5.3) Behaviour: a second long hold returns to the rest state, light off, timer stopped, the stop vibration shown`, async ({ page }) => {
  const w = await boot(page)
  const r = RULES()
  const { rest, rec } = restAndRecording(r)
  await toBehaviour(page)
  await startRecording(page, r, rec)
  const m0 = await marks(page).count()
  const stop = transition(r, rec, 'long_press')
  expect(stop.to, 'control: the record sends the recording state to the rest state on a long press').toBe(rest)

  // does: holds the button again
  await hold(page, Number(process.env.J5_HOLD2_MS ?? HOLD_MS(r)))
  await expectState(page, r, rest, 'after the second long hold')
  await expect(timerEl(page), 'the timer is still showing after the stop').toHaveText('—')
  const stopMarks = marksOf(r, stop.motor_ids)
  await expect(marks(page), "the stop vibration marks are not the record's stop pattern").toHaveCount(m0 + stopMarks.length)
  const all = await marks(page).evaluateAll((els) => els.map((e) => Number(e.getAttribute('data-on-ms'))))
  expect(all.slice(-stopMarks.length), 'the last vibration marks differ from the stop pattern').toEqual(stopMarks)
  // the timer is stopped: the panel's elapsed seconds stay at 0
  await page.waitForTimeout(1300)
  expect((await clockNow(page)).e, 'the elapsed seconds still run after the stop').toBe('0')
  expect(await page.evaluate(() => window.__stage!.lightOn()), 'the 3D ring light stayed on').toBe(false)
  await expectDoesNow(page, r, rest)
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

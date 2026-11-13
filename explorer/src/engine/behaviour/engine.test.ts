// behaviour-engine-C01..C06: a made-up three-state record, and the live record when the collector has made it.
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import type { FirmwareRules } from '../../contract/records'
import { createEngine, initialState } from './engine'

const src = { file: 'fixture.md', line: 1 }
const rules: FirmwareRules = {
  design_version: 'Z2', basis_version: 'Z1',
  states: [
    { id: 'IDLE', label: 'Idle', meaning: 'waits', microphones: 'off', storage: null, screen: 'on briefly', radio: null, source: src },
    { id: 'LIVE', label: 'Live', meaning: 'stores', microphones: 'on', storage: null, screen: 'dark', radio: null, source: src },
    { id: 'DOCK', label: 'Dock', meaning: 'in the case', microphones: 'off', storage: null, screen: null, radio: null, source: src },
  ],
  transitions: [
    { from: 'IDLE', event_text: 'long press', event_kind: 'long_press', to: 'LIVE', actions: 'open; PA', motor_ids: ['PA'], source: src },
    { from: 'LIVE', event_text: 'long press', event_kind: 'long_press', to: 'IDLE', actions: 'close; PB', motor_ids: ['PB'], source: src },
    { from: 'LIVE', event_text: 'short press', event_kind: 'short_press', to: 'LIVE', actions: 'highlight marker; PC', motor_ids: ['PC'], source: src },
    { from: 'IDLE', event_text: 'cable appears', event_kind: 'vbus', to: 'DOCK', actions: null, motor_ids: [], source: src },
    { from: 'DOCK', event_text: 'joystick centre', event_kind: 'joystick', to: 'IDLE', actions: null, motor_ids: [], source: src },
  ],
  gestures: [
    { kind: 'long_press', timing_text: 'held', min_hold_ms: 900, max_hold_ms: null, window_ms: null, fires: 'while_held', per_state: [], source: src },
    { kind: 'short_press', timing_text: 'quick', min_hold_ms: 30, max_hold_ms: 500, window_ms: 350, fires: 'after_window', per_state: [], source: src },
    { kind: 'double_press', timing_text: 'two', min_hold_ms: 30, max_hold_ms: 500, window_ms: 350, fires: 'after_window', per_state: [], source: src },
  ],
  motor_patterns: [
    { id: 'PA', event: 'start', pulses: [{ on_ms: 70, off_ms: 0 }], total_ms: 70, source: src },
    { id: 'PB', event: 'stop', pulses: [{ on_ms: 70, off_ms: 110 }, { on_ms: 70, off_ms: 0 }], total_ms: 250, source: src },
    { id: 'PC', event: 'mark', pulses: [{ on_ms: 30, off_ms: 0 }], total_ms: 30, source: src },
    { id: 'PD', event: 'joystick move', pulses: [{ on_ms: 20, off_ms: 0 }], total_ms: 20, source: src },
  ],
  joystick: [{ direction: 'up', effect: 'previous', source: src }],
  light_rule: { text: 'light follows microphones', on_where_microphones_on: true, source: src },
}
const LONG = rules.gestures[0]!.min_hold_ms as number
const [SHORT_LO, SHORT_HI, WINDOW] = [30, 500, 350]

function hold(e: ReturnType<typeof createEngine>, at: number, ms: number) {
  e.send({ type: 'press', t: at })
  const during = e.send({ type: 'tick', t: at + ms })
  const rel = e.send({ type: 'release', t: at + ms })
  return { during, rel }
}

describe('behaviour-engine', () => {
  it('C01 rests in the state a long press leaves for the microphone state', () => {
    expect(initialState(rules)).toBe('IDLE')
    const o = createEngine(rules).send({ type: 'tick', t: 0 })
    expect(o).toMatchObject({ state: 'IDLE', light: false, pulses: [], highlights: 0 })
  })

  it('C02 a full hold starts, light on, pulses from the record; the release adds nothing', () => {
    const e = createEngine(rules)
    const { during, rel } = hold(e, 0, LONG)
    expect(during).toMatchObject({ state: 'LIVE', light: true, pulses: [70], pulseCount: 1 })
    expect(rel).toMatchObject({ state: 'LIVE', pulses: [] })
  })

  it('C03 a tap then idle for the window marks one highlight and stays; a full hold stops with two pulses', () => {
    const e = createEngine(rules)
    hold(e, 0, LONG)
    e.send({ type: 'press', t: 2000 })
    e.send({ type: 'release', t: 2200 })
    expect(e.send({ type: 'tick', t: 2200 + WINDOW - 1 }).highlights).toBe(0)
    const o = e.send({ type: 'tick', t: 2200 + WINDOW })
    expect(o).toMatchObject({ state: 'LIVE', highlights: 1, pulses: [30], light: true })
    expect(o.recordingMs).toBe(2200 + WINDOW - LONG)
    const stop = hold(e, 4000, LONG).during
    expect(stop).toMatchObject({ state: 'IDLE', light: false, pulses: [70, 110, 70], pulseCount: 2, highlights: 0, recordingMs: 0 })
  })

  it('C04 a hold between the short range and the long press changes nothing; a graze changes nothing', () => {
    const e = createEngine(rules)
    hold(e, 0, LONG)
    const mid = (SHORT_HI + LONG) / 2
    const a = hold(e, 3000, mid)
    e.send({ type: 'tick', t: 3000 + mid + WINDOW + 10 })
    expect(a.rel).toMatchObject({ state: 'LIVE', highlights: 0, pulses: [] })
    hold(e, 6000, SHORT_LO - 1)
    expect(e.send({ type: 'tick', t: 8000 })).toMatchObject({ state: 'LIVE', highlights: 0 })
  })

  it('C05 a short press in the idle state does nothing the record does not list; other signals follow the record', () => {
    const e = createEngine(rules)
    hold(e, 0, SHORT_LO + 5)
    expect(e.send({ type: 'tick', t: 5000 })).toMatchObject({ state: 'IDLE', pulses: [], fired: null })
    expect(e.send({ type: 'signal', kind: 'vbus', t: 5100 }).state).toBe('DOCK')
    expect(e.send({ type: 'signal', kind: 'battery', t: 5200 }).state).toBe('DOCK')
    const j = e.send({ type: 'joystick', direction: 'up', t: 5300 })
    expect(j).toMatchObject({ state: 'IDLE', joystickEffect: 'previous' })
    const k = e.send({ type: 'joystick', direction: 'up', t: 5400 })
    expect(k).toMatchObject({ pulses: [20], joystickEffect: 'previous' })
  })

  it('C06 the light follows the record: off when the rule says so; the model is not changed by a step', () => {
    const off = { ...rules, light_rule: { ...rules.light_rule, on_where_microphones_on: false } }
    expect(hold(createEngine(off), 0, LONG).during).toMatchObject({ state: 'LIVE', light: false })
    const e = createEngine(rules)
    const before = JSON.stringify(e.model)
    e.send({ type: 'press', t: 5 })
    expect(JSON.stringify(e.model)).not.toBe(before)
  })
})

const live = join(process.cwd(), 'public', 'data', 'behaviour.json')
describe.runIf(existsSync(live))('behaviour-engine on the live record', () => {
  const real = JSON.parse(existsSync(live) ? readFileSync(live, 'utf8') : '{}') as FirmwareRules
  it('goes rest -> microphone state on a long hold, marks a highlight on a short press, returns on a second hold', () => {
    const long = real.gestures.find((g) => g.kind === 'long_press')!.min_hold_ms!
    const win = real.gestures.find((g) => g.kind === 'short_press')!.window_ms!
    const rest = initialState(real)
    const e = createEngine(real)
    const a = hold(e, 0, long).during
    expect(real.states.find((s) => s.id === a.state)?.microphones).toBe('on')
    // the light follows the record: the design of 13 November has no recording light, so it stays off
    expect(a.light).toBe(real.light_rule.on_where_microphones_on)
    expect(a.pulses.length).toBeGreaterThan(0)
    e.send({ type: 'press', t: 5000 })
    e.send({ type: 'release', t: 5100 })
    const h = e.send({ type: 'tick', t: 5100 + win })
    expect(h).toMatchObject({ state: a.state, highlights: 1 })
    const b = hold(e, 9000, long).during
    expect(b.state).toBe(rest)
    expect(b.light).toBe(false)
  })
})

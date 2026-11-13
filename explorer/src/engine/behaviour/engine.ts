// The behaviour engine: a pure interpreter of the firmware rules record (behaviour.json).
// It holds no rule of its own: every state id, duration and effect is read from the record it is given.
import type { FirmwareRules } from '../../contract/records'

type Rules = FirmwareRules
type Transition = Rules['transitions'][number]
export type EventKind = Transition['event_kind']

/** An input. Times are in milliseconds on one clock; they never go backwards. */
export type EngineEvent =
  | { type: 'press'; t: number }
  | { type: 'release'; t: number }
  | { type: 'tick'; t: number }
  | { type: 'joystick'; direction: string; t: number }
  | { type: 'signal'; kind: EventKind; t: number; text?: string }

export interface Model {
  state: string
  now: number
  pressedAt: number | null
  longFired: boolean
  /** a short press whose second-press window is still open */
  pending: { releasedAt: number } | null
  /** the press now held began inside an open window: it may become a double press */
  secondPress: boolean
  micSince: number | null
  highlights: number
}

export interface Outputs {
  state: string
  light: boolean
  /** the pattern started by this input: on, off, on ... in ms; empty when none */
  pulses: number[]
  pulseCount: number
  highlights: number
  recordingMs: number
  screen: string | null
  /** the transition this input fired, or null */
  fired: Transition | null
  /** what the joystick direction does, from the record's table, or null */
  joystickEffect: string | null
}

function micOn(rules: Rules, state: string): boolean {
  return rules.states.find((s) => s.id === state)?.microphones === 'on'
}

/** The state the ring rests in: the one a long press leaves for a microphone state that a long press leaves back. */
export function initialState(rules: Rules): string {
  const longs = rules.transitions.filter((x) => x.event_kind === 'long_press' && x.from !== x.to)
  for (const x of longs) {
    if (micOn(rules, x.to) && longs.some((y) => y.from === x.to && y.to === x.from)) return x.from
  }
  return rules.states[0]?.id ?? ''
}

export function initialModel(rules: Rules, state?: string): Model {
  return { state: state ?? initialState(rules), now: 0, pressedAt: null, longFired: false, pending: null, secondPress: false, micSince: null, highlights: 0 }
}

function flatten(rules: Rules, ids: string[]): number[] {
  const out: number[] = []
  for (const id of ids) {
    const p = rules.motor_patterns.find((m) => m.id === id)
    if (!p) continue
    for (const x of p.pulses) {
      out.push(x.on_ms)
      if (x.off_ms > 0) out.push(x.off_ms)
    }
  }
  return out
}

interface Work { m: Model; fired: Transition | null; pulses: number[] }

function fire(rules: Rules, w: Work, kind: EventKind, t: number, text?: string): void {
  const tr = rules.transitions.find((x) => x.from === w.m.state && x.event_kind === kind && (!text || x.event_text.includes(text)))
  if (!tr) return
  const m = w.m
  const wasMic = micOn(rules, m.state)
  m.state = tr.to
  const isMic = micOn(rules, tr.to)
  if (isMic && (!wasMic || m.micSince === null)) { m.micSince = t; m.highlights = 0 }
  if (!isMic) { m.micSince = null; m.highlights = 0 }
  if (isMic && /highlight/i.test(tr.actions ?? '')) m.highlights += 1
  w.fired = tr
  w.pulses = flatten(rules, tr.motor_ids)
}

function advance(rules: Rules, w: Work, t: number): void {
  const m = w.m
  const g = (k: EventKind) => rules.gestures.find((x) => x.kind === k)
  const long = g('long_press')
  const short = g('short_press')
  if (m.pressedAt !== null && !m.longFired && long?.min_hold_ms != null && t - m.pressedAt >= long.min_hold_ms) {
    m.longFired = true
    m.secondPress = false
    fire(rules, w, 'long_press', m.pressedAt + long.min_hold_ms)
  }
  if (m.pending && short?.window_ms != null && t - m.pending.releasedAt >= short.window_ms) {
    m.pending = null
    fire(rules, w, 'short_press', t)
  }
}

/** One step. Returns a new model and what this input made the ring do. The inputs are not changed. */
export function step(rules: Rules, before: Model, ev: EngineEvent): { model: Model; outputs: Outputs } {
  const w: Work = { m: { ...before }, fired: null, pulses: [] }
  const m = w.m
  const t = Math.max(ev.t, m.now)
  advance(rules, w, t)
  m.now = t
  const short = rules.gestures.find((x) => x.kind === 'short_press')
  let joystickEffect: string | null = null
  if (ev.type === 'press') {
    if (m.pressedAt === null) {
      m.secondPress = m.pending !== null
      m.pending = null
      m.pressedAt = t
      m.longFired = false
    }
  } else if (ev.type === 'release') {
    if (m.pressedAt !== null) {
      const held = t - m.pressedAt
      const wasLong = m.longFired
      const second = m.secondPress
      m.pressedAt = null
      m.longFired = false
      m.secondPress = false
      const inRange = short?.min_hold_ms != null && short.max_hold_ms != null && held >= short.min_hold_ms && held <= short.max_hold_ms
      if (!wasLong && inRange) {
        if (second) fire(rules, w, 'double_press', t)
        else m.pending = { releasedAt: t }
      }
    }
  } else if (ev.type === 'joystick') {
    joystickEffect = rules.joystick.find((j) => j.direction === ev.direction)?.effect ?? null
    fire(rules, w, 'joystick', t)
    if (!w.fired) w.pulses = flatten(rules, rules.motor_patterns.filter((p) => /joystick/i.test(p.event)).map((p) => p.id))
  } else if (ev.type === 'signal') {
    fire(rules, w, ev.kind, t, ev.text)
  }
  const st = rules.states.find((s) => s.id === m.state)
  const outputs: Outputs = {
    state: m.state,
    light: !!rules.light_rule.on_where_microphones_on && st?.microphones === 'on',
    pulses: w.pulses,
    pulseCount: w.pulses.length === 0 ? 0 : countOn(rules, w),
    highlights: m.highlights,
    recordingMs: m.micSince === null ? 0 : t - m.micSince,
    screen: st?.screen ?? null,
    fired: w.fired,
    joystickEffect,
  }
  return { model: m, outputs }
}

function countOn(rules: Rules, w: Work): number {
  if (w.fired) return w.fired.motor_ids.reduce((n, id) => n + (rules.motor_patterns.find((p) => p.id === id)?.pulses.length ?? 0), 0)
  return rules.motor_patterns.filter((p) => /joystick/i.test(p.event)).reduce((n, p) => n + p.pulses.length, 0)
}

/** A small holder around step for a screen: engine.send(event) returns the outputs. */
export function createEngine(rules: Rules, state?: string) {
  let model = initialModel(rules, state)
  return {
    send(ev: EngineEvent): Outputs {
      const r = step(rules, model, ev)
      model = r.model
      return r.outputs
    },
    get model(): Model { return model },
    reset(to?: string): void { model = initialModel(rules, to) },
  }
}

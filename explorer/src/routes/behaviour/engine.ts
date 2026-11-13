// The ONE adapter between the Behaviour screen and the behaviour engine (src/engine/behaviour). The
// screen holds no rule of its own: it keeps a log of presses with their times and asks the engine, which
// reads every state, hold time and effect from the firmware-rules record, what the ring does now.
import { initialModel, step, type EngineEvent, type Model, type Outputs } from '../../engine/behaviour'
import type { FirmwareRules } from '../../contract'

export type RingEvent =
  | { kind: 'press'; t: number }
  | { kind: 'release'; t: number }
  | { kind: 'joystick'; t: number; direction: string }

export interface Pulse {
  key: string
  at: number
  onMs: number
}

export interface EngineOutput {
  state: string
  light: boolean
  highlights: number
  /** ms since the recording began; null while the microphones are off */
  recordingMs: number | null
  /** one entry per pulse of the vibration motor, with the time it started (same clock as the events) */
  pulses: Pulse[]
  /** a press is down: how long it has been held, how long the long press needs, and whether it already fired */
  hold: { heldMs: number; needMs: number | null; fired: boolean } | null
  /** what the joystick did last, from the record */
  note: string | null
}

export const EMPTY: EngineOutput = { state: '', light: false, highlights: 0, recordingMs: null, pulses: [], hold: null, note: null }

const toEngine = (e: RingEvent): EngineEvent => (e.kind === 'joystick' ? { type: 'joystick', direction: e.direction, t: e.t } : { type: e.kind, t: e.t })

/** Replay the whole log, then look at `now`. Pure: the same log and clock give the same answer. */
export function run(rules: FirmwareRules, events: readonly RingEvent[], now: number): EngineOutput {
  let model: Model = initialModel(rules)
  const pulses: Pulse[] = []
  let note: string | null = null
  const feed = (ev: EngineEvent, tag: string): Outputs => {
    const r = step(rules, model, ev)
    model = r.model
    if (r.outputs.pulses.length) {
      let at = ev.t
      r.outputs.pulses.forEach((ms, i) => {
        if (i % 2 === 0) pulses.push({ key: `${tag}-${i}`, at, onMs: ms })
        at += ms
      })
    }
    if (r.outputs.joystickEffect) note = r.outputs.joystickEffect
    return r.outputs
  }
  events.forEach((e, i) => feed(toEngine(e), String(i)))
  const o = feed({ type: 'tick', t: Math.max(now, model.now) }, 'tick')
  const need = rules.gestures.find((g) => g.kind === 'long_press')?.min_hold_ms ?? null
  const mic = rules.states.find((s) => s.id === o.state)?.microphones === 'on'
  return {
    state: o.state,
    light: o.light,
    highlights: o.highlights,
    recordingMs: mic ? o.recordingMs : null,
    pulses,
    hold: model.pressedAt === null ? null : { heldMs: model.now - model.pressedAt, needMs: need, fired: model.longFired },
    note,
  }
}

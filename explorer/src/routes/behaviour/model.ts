// Pure derivations for the Behaviour screen. No ring value is written here: names, times and effects
// come from the firmware-rules record; the words below are the screen's own labels.
import type { FirmwareRules, RingModel } from '../../contract'

export const WORDS = {
  title: 'How the ring behaves',
  state: 'State now',
  light: 'Light',
  timer: 'Recording',
  highlights: 'Highlights',
  vibration: 'Vibration',
  nothingYet: 'Nothing yet',
  joystick: 'Joystick',
  centre: 'Centre press of the joystick',
  centreLead: 'Press the centre. Hold it, or tap it.',
  states: 'All states',
  now: 'Now',
  doesNow: 'What a press does now',
  lightOn: 'on',
  lightOff: 'off',
} as const

type Rule = FirmwareRules['states'][number]

export const stateOf = (rules: FirmwareRules, id: string): Rule | undefined => rules.states.find((s) => s.id === id)

const words = (t: string): string[] => t.toLowerCase().match(/[a-z]{5,}/g) ?? []
const hasId = (label: string, id: string): boolean => new RegExp(`(^|[^A-Za-z0-9_])${id}([^A-Za-z0-9_]|$)`).test(label)

/** The screen of the ring (a `ring-model` screen state) that shows while the ring is in a firmware state:
 *  the screen labelled with the state's id, else the one the state's screen text points at by another
 *  state id in backticks, else the one whose label shares a long word with that text. null = screen off. */
export function screenFor(rules: FirmwareRules, ring: RingModel, state: string, depth = 0): string | null {
  const screens = ring.screens.states
  const byId = screens.find((s) => hasId(s.label, state))
  if (byId) return byId.state
  const text = rules.states.find((s) => s.id === state)?.screen ?? ''
  const ref = depth < 2 ? rules.states.find((s) => s.id !== state && text.includes('`' + s.id + '`')) : undefined
  if (ref) return screenFor(rules, ring, ref.id, depth + 1)
  const w = new Set(words(text))
  return screens.find((s) => words(s.label).some((x) => w.has(x)))?.state ?? null
}

export function clock(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000))
  const p = (n: number) => String(n).padStart(2, '0')
  return `${p(Math.floor(s / 3600))}:${p(Math.floor((s % 3600) / 60))}:${p(s % 60)}`
}

/** What each gesture does in this state, in the record's words. */
export function effectsIn(rules: FirmwareRules, state: string): { kind: string; timing: string; effect: string }[] {
  return rules.gestures.flatMap((g) => g.per_state.filter((p) => p.state === state).map((p) => ({ kind: g.kind.replace(/_/g, ' '), timing: g.timing_text, effect: p.effect })))
}

type Joy = FirmwareRules['joystick'][number]
const AREA: [RegExp, string][] = [
  [/\b(up|top|north)\b/i, 'n'],
  [/\b(down|bottom|south)\b/i, 's'],
  [/\b(left|west|hand)\b/i, 'w'],
  [/\b(right|east|fingertip)\b/i, 'e'],
]
/** Place a joystick direction on a plus-shaped pad by the words of its name; anything else is the centre. */
export function padArea(j: Joy): 'n' | 's' | 'w' | 'e' | 'c' {
  const hit = AREA.find(([re]) => re.test(j.direction))
  return (hit?.[1] as 'n' | 's' | 'w' | 'e' | undefined) ?? 'c'
}

const num = (n: number): string => (n >= 1000 && n % 1000 === 0 ? `${n / 1000} s` : `${n} ms`)
/** The short hint beside the joystick's centre press, built from the record's numbers; the full sentence is the tooltip. */
export function holdHints(rules: FirmwareRules): { text: string; title: string }[] {
  return rules.gestures.flatMap((g) => {
    if (g.kind === 'long_press' && g.min_hold_ms != null) return [{ text: `Hold ${num(g.min_hold_ms)}`, title: g.timing_text }]
    if (g.kind === 'short_press' && g.min_hold_ms != null && g.max_hold_ms != null) return [{ text: `Tap ${g.min_hold_ms} to ${num(g.max_hold_ms)}`, title: g.timing_text }]
    return []
  })
}

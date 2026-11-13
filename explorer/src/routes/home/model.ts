// Pure derivations for the Home screen. No ring value is written here: every string comes from the bundle.
import type { AreaStates, Fact, OpenItems, RouteId } from '../../contract'

type AreaRecord = AreaStates['areas'][number]

/** The words Home itself owns (the contract owns the state and banner words). */
export const HOME_WORDS = {
  title: 'The ring at a glance',
  keyNumbers: 'Key numbers',
  areas: 'The 8 areas',
  next: 'What is next for you',
  notKnown: 'not known yet for this ring',
  source: 'Source',
  notListed: 'not in the files list',
} as const

/** The text of one fact: its value, with the unit added only when the value does not already carry it. */
export function factText(f: Pick<Fact, 'value' | 'unit'>): string {
  const v = String(f.value)
  const u = f.unit
  if (!u) return v
  return v.toLowerCase().includes(u.toLowerCase()) ? v : `${v} ${u}`
}

export interface LeftOut {
  name: string
  reason: string
}

/** Facts the collector left out on purpose. Its reason is in the manifest message of the record:
 *  "Left out, not readable: <name>: <reason>" (several are separated by "; "). */
export function leftOut(message: string | null | undefined): LeftOut[] {
  const prefix = 'Left out, not readable: '
  if (!message || !message.startsWith(prefix)) return []
  const out: LeftOut[] = []
  for (const part of message.slice(prefix.length).split('; ')) {
    const i = part.indexOf(': ')
    if (i <= 0) continue
    out.push({ name: part.slice(0, i), reason: part.slice(i + 2) })
  }
  return out
}

export const capitalise = (s: string): string => (s ? s[0]!.toUpperCase() + s.slice(1) : s)

export interface NextItem {
  key: string
  title: string
  line: string
  to: RouteId | null
}

/** The open items whose owner is the owner; when there are none, the next supplier asks. */
export function nextItems(
  areas: readonly AreaRecord[] | null,
  open: OpenItems | null,
  label: (id: RouteId) => string,
  max = 4,
): NextItem[] {
  const mine = (areas ?? [])
    .filter((a) => a.who === 'owner' && a.state !== 'done')
    .map((a) => ({ key: `area-${a.id}`, title: label(a.id), line: a.why ?? '', to: a.id as RouteId | null }))
  if (mine.length) return mine.slice(0, max)
  return (open?.supplier_requests ?? []).slice(0, max).map((s) => ({
    key: `ask-${s.id}`,
    title: `${s.item} (${s.who})`,
    line: s.ask,
    to: 'open' as RouteId | null,
  }))
}


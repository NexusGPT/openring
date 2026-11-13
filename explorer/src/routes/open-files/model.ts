// Open items: the four lists as one list of rows, the filter, the supplier chips. Pure; the words on
// screen that are not bundle values live in OPEN_WORDS and nowhere else.
import type { OpenItems } from '../../contract'

export const OPEN_WORDS = {
  title: 'Open items and files',
  open: 'Open items',
  files: 'Files',
  nothing: 'nothing waiting',
  nothingHere: 'nothing here',
  everyone: 'Everyone',
} as const

export type FilterId = 'all' | 'supplier' | 'bench' | 'risk' | 'decision'
export type GroupId = Exclude<FilterId, 'all'>

/** Chips in the order the owner reads them. `waiting on a supplier` is the area-state word. */
export const FILTERS: readonly { id: FilterId; label: string }[] = [
  { id: 'all', label: 'all' },
  { id: 'supplier', label: 'waiting on a supplier' },
  { id: 'bench', label: 'bench tests' },
  { id: 'risk', label: 'risks' },
  { id: 'decision', label: 'decisions' },
]

export const GROUP_TITLE: Record<GroupId, string> = {
  supplier: 'Waiting on a supplier',
  bench: 'Bench tests',
  risk: 'Risks',
  decision: 'Your decisions',
}
const GROUP_ORDER: readonly GroupId[] = ['supplier', 'bench', 'risk', 'decision']

export interface Source {
  file: string
  line: number | null
}

export type Row =
  | { group: 'supplier'; id: string; title: string; who: string; ask: string; section: string; source: Source }
  | { group: 'bench'; id: string; title: string; detail: string | null; source: Source }
  | { group: 'risk'; id: string; text: string; source: Source }
  | { group: 'decision'; id: string; date: string; speaker: string; quote: string; source: Source }

export interface Group {
  id: GroupId
  title: string
  rows: Row[]
}

/** Decisions newest first; the other groups keep the order of the file. */
export function groupsOf(o: OpenItems): Group[] {
  const decisions = [...o.decisions].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))
  const rows: Record<GroupId, Row[]> = {
    supplier: o.supplier_requests.map((s) => ({ group: 'supplier', id: s.id, title: s.item, who: s.who, ask: s.ask, section: s.section, source: s.source })),
    bench: o.bench_tests.map((b) => ({ group: 'bench', id: b.id, title: b.title, detail: b.detail, source: b.source })),
    risk: o.risks.map((r) => ({ group: 'risk', id: r.id, text: r.text, source: r.source })),
    decision: decisions.map((d, i) => ({ group: 'decision', id: `${d.date}#${i}`, date: d.date, speaker: d.speaker, quote: d.quote, source: d.source })),
  }
  return GROUP_ORDER.map((id) => ({ id, title: GROUP_TITLE[id], rows: rows[id] }))
}

/** The groups a chip leaves on screen; with `who` set, only the supplier rows of that supplier. */
export function applyFilter(groups: Group[], filter: FilterId, who: string | null): Group[] {
  const kept = filter === 'all' ? groups : groups.filter((g) => g.id === filter)
  if (filter !== 'supplier' || !who) return kept
  return kept.map((g) => ({ ...g, rows: g.rows.filter((r) => r.group === 'supplier' && r.who === who) }))
}

/** The distinct suppliers, in first-seen order. */
export function suppliersOf(groups: Group[]): string[] {
  const seen: string[] = []
  for (const r of groups.find((g) => g.id === 'supplier')?.rows ?? []) if (r.group === 'supplier' && !seen.includes(r.who)) seen.push(r.who)
  return seen
}

export const countOf = (groups: Group[], id: FilterId): number => (id === 'all' ? groups.reduce((n, g) => n + g.rows.length, 0) : (groups.find((g) => g.id === id)?.rows.length ?? 0))

// Pure derivations for the Case screen. No ring or case fact is written here: names, numbers and parts
// come from the bundle (case, parts, part-notes). The words below are the screen's own labels.
import type { Case, Fact, Parts, PartsLine } from '../../contract'

export const WORDS = {
  title: 'The charging case',
  numbers: 'Key numbers',
  lid: 'Lid',
  openLid: 'Open the lid',
  closeLid: 'Close the lid',
  lidHint: 'Opening the lid shows the ring seated on its pins.',
  parts: 'Parts of the case',
  listLine: 'On the parts list',
  supplier: 'Asked of suppliers',
  linesOf: 'lines',
  partsOf: 'parts',
  noModel: 'No 3D model of the case yet. The numbers and parts below are still the bundle’s.',
  onBoard: 'On the',
  openBoard: 'Open this board',
  boardParts: 'Parts on this board',
  noLine: 'This solid has no parts-list line',
  model: 'Model',
  refit: 'From the design files',
} as const

export type CaseLine = NonNullable<Case['lines']>[number]
export type CaseBoard = NonNullable<Case['boards']>[number]

/** The counts line: "<n> parts-list lines: a in the 3D model, b on the boards, c not fitted, d without a solid". Null without counts. */
export function countsLine(c: Case | null): string | null {
  const n = c?.counts
  if (!n) return null
  return `${n.lines} parts-list lines: ${n.solid} in the 3D model, ${n.board} on the boards, ${n.not_fitted} not fitted, ${n.no_solid} without a solid`
}

/** The class of one parts-list line of the case record, by any of its part ids. */
export const caseLineOf = (c: Case | null, id: string | null): CaseLine | null => (id ? c?.lines?.find((l) => l.part_ids.includes(id)) ?? null : null)

/** The solid that stands for a part id (the first one that holds it). */
export const nodeOf = (c: Case | null, id: string | null): { name: string; part_ids: string[] } | null => (id ? c?.glb?.nodes.find((n) => n.part_ids.includes(id)) ?? null : null)

/** The board whose solid this is, if it is one. */
export const boardOfNode = (c: Case | null, node: string | null): CaseBoard | null => (node ? c?.boards?.find((b) => b.node === node) ?? null : null)

/** The boards that carry a line: keys named by the line. */
export const boardsOfLine = (c: Case | null, l: CaseLine | null): CaseBoard[] => (l ? (c?.boards ?? []).filter((b) => l.boards.includes(b.key)) : [])

/** Plain words for the class of a line, in the data's own board titles. */
export function classWords(c: Case | null, l: CaseLine): string {
  if (l.class === 'solid') return '3D'
  if (l.class === 'board') return boardsOfLine(c, l).map((b) => b.title.toLowerCase()).join(' + ') || 'board'
  if (l.class === 'not-fitted') return 'not fitted'
  return 'no solid'
}

/** How far the lid swings when it is shown open: a viewing angle, not a case fact. */
export const OPEN_DEG = 120

/** The text of one fact: its value, with the unit added only when the value does not already carry it. */
export function factText(f: Pick<Fact, 'value' | 'unit'>): string {
  const v = String(f.value)
  const u = f.unit
  if (!u) return v
  return v.toLowerCase().includes(u.toLowerCase()) ? v : `${v} ${u}`
}

/** The parts-list lines of the case, in the order of the case record's part ids (each line once). */
export function caseLines(c: Case | null, parts: Parts | null): PartsLine[] {
  if (!parts) return []
  const wanted = new Set(c?.part_ids ?? [])
  const lines = parts.lines.filter((l) => l.bom === 'case')
  return wanted.size ? lines.filter((l) => l.part_ids.some((id) => wanted.has(id))) : lines
}

/** Hover-tag names for the stage: node name -> what the part is, from the parts line it carries. */
export function nodeNames(c: Case | null, parts: Parts | null): Record<string, string> {
  const out: Record<string, string> = {}
  for (const n of c?.glb?.nodes ?? []) {
    const line = parts?.lines.find((l) => n.part_ids.length > 0 && l.part_ids.includes(n.part_ids[0]!))
    out[n.name] = line ? (line.function ?? line.item) : n.name.replace(/_/g, ' ')
  }
  return out
}

// Pure helpers of the Board screen. No ring value is written here: every name, size and side comes from the bundle.
import type { BoardFiles, PartNotes, PartPlacements, Parts, PartsLine } from '../../contract'

export type Placement = BoardFiles['placements'][number]
export type Side = Placement['side']
export type Mode = 'top' | 'bottom' | 'both'
export const MODES: readonly { id: Mode; label: string }[] = [
  { id: 'top', label: 'Top' },
  { id: 'bottom', label: 'Bottom' },
  { id: 'both', label: 'Both' },
]
export const shows = (mode: Mode, side: Side): boolean => mode === 'both' || mode === side

export interface Box { x: number; y: number; w: number; h: number }
/** A board read from a KiCad board file counts y downwards (as KiCad draws it); a plan made from the design's
 *  placement table counts y upwards. The outline's source file tells which one the record holds. */
export const yDown = (board: BoardFiles): boolean => /\.kicad_pcb$/i.test(board.outline?.source.file ?? '')
/** Drawing coordinates (y down on the screen): the plan then reads as seen from above in both cases. */
export const topOf = (b: Box, down: boolean): number => (down ? b.y - b.h / 2 : -(b.y + b.h / 2))
export const left = (b: Box): number => b.x - b.w / 2

/** The viewBox that holds the outline, the cut-outs and every part, with a margin in mm. */
export function viewBoxOf(board: BoardFiles, margin = 2): readonly [number, number, number, number] | null {
  const boxes: Box[] = [...(board.outline ? [board.outline] : []), ...board.placements, ...(board.notches ?? [])]
  if (boxes.length === 0) return null
  const down = yDown(board)
  const x0 = Math.min(...boxes.map(left))
  const y0 = Math.min(...boxes.map((b) => topOf(b, down)))
  const x1 = Math.max(...boxes.map((b) => left(b) + b.w))
  const y1 = Math.max(...boxes.map((b) => topOf(b, down) + b.h))
  return [x0 - margin, y0 - margin, x1 - x0 + 2 * margin, y1 - y0 + 2 * margin]
}

/** The part id of a placed object: the board record's own, else the part note that names this model object. */
export function partIdOf(p: Placement, notes: PartNotes['notes'] | null): string | null {
  if (p.part_id) return p.part_id
  for (const [id, n] of Object.entries(notes ?? {})) if (id.startsWith('ring:') && n.model_names.includes(p.name)) return id
  return null
}

export const lineOf = (parts: Parts | null, id: string | null): PartsLine | null => (id ? parts?.lines.find((l) => l.part_ids.includes(id)) ?? null : null)
export const spaced = (name: string): string => name.replace(/[_-]+/g, ' ').trim()

/** Words for a placed object: its parts-list item, else its note's name, else its own name with spaces. */
export function labelOf(p: Placement, parts: Parts | null, notes: PartNotes['notes'] | null): string {
  const id = partIdOf(p, notes)
  return lineOf(parts, id)?.item ?? (id ? notes?.[id]?.what : null) ?? spaced(p.name)
}

/** The layer of the 3D model that holds the circuit board: the layer most of the placed objects sit in. An object
 *  is found in the model by its own name, else by the model names its part note lists. */
export function boardLayerId(board: BoardFiles | null, placements: PartPlacements | null, notes: PartNotes['notes'] | null): string | null {
  if (!board || !placements) return null
  const count = new Map<string, number>()
  for (const p of board.placements) {
    const names = [p.name, ...(notes?.[partIdOf(p, notes) ?? '']?.model_names ?? [])]
    const layer = placements.placements.find((x) => names.includes(x.name))?.layer
    if (layer) count.set(layer, (count.get(layer) ?? 0) + 1)
  }
  let best: string | null = null
  let most = 0
  for (const [layer, n] of count) if (n > most) { best = layer; most = n }
  return best
}

/** mm with at most one decimal: 27 -> '27', 17.4 -> '17.4'. */
export const mm = (n: number): string => String(Number(n.toFixed(1)))
export const countSide = (board: BoardFiles, side: Side): number => board.placements.filter((p) => p.side === side).length

/** Objects whose centre lies outside the board outline: parts the design has not placed on the board yet. */
export function outsideCount(board: BoardFiles): number {
  const o = board.outline
  if (!o) return 0
  return board.placements.filter((p) => Math.abs(p.x - o.x) > o.w / 2 || Math.abs(p.y - o.y) > o.h / 2).length
}

const fold = (s: string): string => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
/** Plain-text match on the words, the object's name and the part's reference. */
export const matchesQuery = (q: string, ...fields: string[]): boolean => {
  const t = fold(q.trim())
  return !t || fields.some((f) => fold(f).includes(t))
}

// ---- the board list (board-files.boards): the picker, the plan of one board, its copper layers ----
export type BoardEntry = NonNullable<BoardFiles['boards']>[number]
export type LayerEntry = BoardEntry['layers'][number]
export interface BoardGroup {
  id: string
  title: string
  entries: BoardEntry[]
}

/** The picker groups, in the order of the list: one button per group; a band circuit group holds one entry per ring size. */
export function groupsOf(boards: readonly BoardEntry[] | null | undefined): BoardGroup[] {
  const out: BoardGroup[] = []
  for (const b of boards ?? []) {
    const g = out.find((x) => x.id === b.group)
    if (g) g.entries.push(b)
    else out.push({ id: b.group, title: b.title, entries: [b] })
  }
  return out
}

/** The entry of a group for a ring size label ('US 9'); the first entry when the size is not given or not there. */
export function pickEntry(g: BoardGroup, size: string | null): BoardEntry {
  return g.entries.find((e) => e.size_label !== null && e.size_label === size) ?? (g.entries[0] as BoardEntry)
}

/** The plan-shaped record of one board entry, so the same plan drawing serves every board. Part names are the references. */
export function planOf(e: BoardEntry): BoardFiles {
  return {
    routed: e.state.status === 'routed-checked',
    outline: e.outline,
    svg: { top: null, bottom: null },
    placements: e.placements.map((p) => ({ name: p.ref, part_id: p.part_id, x: p.x, y: p.y, w: p.w, h: p.h, side: p.side })),
    missing: e.missing,
  }
}

/** 'all' stacks every copper layer, 'none' shows the outline and the parts only, else one layer by its id. */
export type LayerChoice = string
export function layerChoice(e: BoardEntry | null, param: string | null): LayerChoice {
  if (!e || e.layers.length === 0) return 'none'
  if (param === 'all' || param === 'none') return param
  return e.layers.some((l) => l.id === param) ? (param as string) : (e.layers[0] as LayerEntry).id
}

/** The layer pictures to draw, the bottom layer first so the top layer lies over it. */
export function layersShown(e: BoardEntry | null, choice: LayerChoice): LayerEntry[] {
  if (!e || choice === 'none') return []
  const withPicture = e.layers.filter((l) => l.svg)
  if (choice === 'all') return [...withPicture].reverse()
  return withPicture.filter((l) => l.id === choice)
}

/** The value of a placed part on a board entry, if the file names one. */
export const valueOf = (e: BoardEntry | null, ref: string): string | null => e?.placements.find((p) => p.ref === ref)?.value ?? null

/** A date and time 'YYYY-MM-DD HH:MM' as the bundle writes it, in words: '13 Nov 2026, 06:41'. */
export function stampWords(s: string | null | undefined): string | null {
  const m = s?.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/)
  if (!m) return s ?? null
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${Number(m[3])} ${months[Number(m[2]) - 1] ?? m[2]} ${m[1]}, ${m[4]}:${m[5]}`
}

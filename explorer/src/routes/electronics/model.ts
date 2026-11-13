// Pure helpers of the Electronics screen. No ring value is written here: every name, count and label
// comes from the bundle records passed in.
import type { Electronics, Files, PartNotes, Parts, PartsLine, SchematicPages } from '../../contract'

export type Block = Electronics['blocks'][number]
export type Link = Electronics['links'][number]
export type Page = SchematicPages['pages'][number]
export type Notes = PartNotes['notes']

const base = (p: string): string => (p.split('/').pop() ?? p).replace(/\.[^.]+$/, '')

/** The wiring-diagram page of a block: the page named by the block's sheet, else by its id, else by its
 *  title, else the page that shares the most parts with it. */
export function pageOfBlock(b: Block, pages: SchematicPages | null): Page | null {
  const list = pages?.pages ?? []
  const byKey = (k: string) => list.find((p) => p.id === k || base(p.source.file) === base(k))
  const hit = byKey(b.sheet) ?? byKey(b.id) ?? list.find((p) => p.title === b.label)
  if (hit) return hit
  let best: Page | null = null
  let most = 0
  for (const p of list) {
    const n = p.part_ids.filter((id) => b.part_ids.includes(id)).length
    if (n > most) { best = p; most = n }
  }
  return best
}

export function blockOfPage(p: Page, blocks: readonly Block[], pages: SchematicPages | null): Block | null {
  return blocks.find((b) => pageOfBlock(b, pages)?.id === p.id) ?? null
}

/** Part ids shown for a block: the ones its page lists, plus the ones the block lists. */
export function partIdsOf(b: Block | null, p: Page | null): string[] {
  const out: string[] = []
  for (const id of [...(p?.part_ids ?? []), ...(b?.part_ids ?? [])]) if (!out.includes(id)) out.push(id)
  return out
}

export interface Placed {
  id: string
  col: 'left' | 'mid' | 'right'
  /** percent of the diagram height, centre of the block */
  y: number
}

/** The block with most links sits in the middle; the others fill a left column, then a right one. */
export function layoutBlocks(blocks: readonly Block[], links: readonly Link[]): { placed: Placed[]; rows: number } {
  if (blocks.length === 0) return { placed: [], rows: 0 }
  const degree = (id: string) => new Set(links.flatMap((l) => (l.from === id ? [l.to] : l.to === id ? [l.from] : []))).size
  const hub = blocks.reduce((a, b) => (degree(b.id) > degree(a.id) ? b : a), blocks[0]!)
  const rest = blocks.filter((b) => b.id !== hub.id)
  const nLeft = Math.ceil(rest.length / 2)
  const rows = Math.max(nLeft, rest.length - nLeft, 1)
  const place = (b: Block, i: number, n: number, col: Placed['col']): Placed => ({ id: b.id, col, y: ((i + 0.5 + (rows - n) / 2) / rows) * 100 })
  return {
    rows,
    placed: [
      { id: hub.id, col: 'mid', y: 50 },
      ...rest.slice(0, nLeft).map((b, i) => place(b, i, nLeft, 'left')),
      ...rest.slice(nLeft).map((b, i) => place(b, i, rest.length - nLeft, 'right')),
    ],
  }
}

export const linksOf = (id: string, links: readonly Link[]): { other: string; nets: string[] }[] =>
  links.flatMap((l) => (l.from === id ? [{ other: l.to, nets: l.nets }] : l.to === id ? [{ other: l.from, nets: l.nets }] : []))

export const hubOf = (blocks: readonly Block[], links: readonly Link[]): Block | null => {
  const first = layoutBlocks(blocks, links).placed[0]
  return blocks.find((b) => b.id === first?.id) ?? null
}

export const lineOfId = (parts: Parts | null, id: string): PartsLine | null => parts?.lines.find((l) => l.part_ids.includes(id)) ?? null
export const refOf = (id: string): string => id.slice(id.indexOf(':') + 1)

/** Words for a part row: its parts-list item, else its note's name, else its reference. */
export const partLabel = (id: string, parts: Parts | null, notes: Notes | null): string => lineOfId(parts, id)?.item ?? notes?.[id]?.what ?? refOf(id)

/** A PDF of the wiring diagram listed in the files list, for the days the pictures are not built. */
export function fallbackPdf(files: Files | null): string | null {
  return files?.files.find((f) => f.area === 'electronics' && /\.pdf$/i.test(f.path))?.path ?? null
}
export const isListed = (files: Files | null, path: string | null | undefined): boolean => !!path && !!files?.files.some((f) => f.path === path)

const fold = (s: string): string => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
/** Rows of a table that contain the typed text in any cell. Plain text comparison, never a pattern. */
export function filterRows(rows: readonly string[][], q: string): string[][] {
  const t = fold(q.trim())
  return t ? rows.filter((r) => r.some((c) => fold(c).includes(t))) : [...rows]
}

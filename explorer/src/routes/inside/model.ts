// Pure helpers of the Inside screen. No ring value is written here: names, layers and counts all come
// from the bundle records passed in.
import type { PartNotes, PartPlacements, Parts, PartsLine, RingModel } from '../../contract'

export type Notes = PartNotes['notes']
export const MAX_RESULTS = 8

/** Lower case, accents removed: 'Würth' and 'wurth' read the same. */
export function fold(s: string): string {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

export interface SearchHit {
  /** the part id a choice selects */
  id: string
  line: PartsLine
  /** why it matched, for the order of the list: lower is better */
  rank: number
}

/** The ring's parts-list lines (Inside never lists the case). */
export const ringLines = (parts: Parts | null): PartsLine[] => (parts?.lines ?? []).filter((l) => l.bom === 'ring')

/** Substring search, never a pattern: the text typed is only ever compared as text. */
export function searchParts(lines: readonly PartsLine[], notes: Notes | null, query: string): SearchHit[] {
  const q = fold(query.trim())
  if (!q) return []
  const hits: SearchHit[] = []
  for (const line of lines) {
    const refIdx = line.refs.findIndex((r) => fold(r).includes(q))
    const exactRef = line.refs.some((r) => fold(r) === q)
    const note = line.part_ids.map((id) => notes?.[id]).find(Boolean)
    const fields: (string | null | undefined)[] = [line.item, line.maker, line.maker_part_number, note?.what, note?.why]
    const fieldIdx = fields.findIndex((f) => f != null && fold(f).includes(q))
    if (refIdx < 0 && fieldIdx < 0) continue
    const id = (refIdx >= 0 ? line.part_ids[refIdx] : undefined) ?? line.part_ids[0]
    if (!id) continue
    hits.push({ id, line, rank: exactRef ? 0 : refIdx >= 0 ? 1 : 2 + fieldIdx })
  }
  return hits.sort((a, b) => a.rank - b.rank).slice(0, MAX_RESULTS)
}

export interface LayerRow {
  id: string
  label: string
  count: number
}

/** One row per layer of the record, in the record's order, with the number of placed parts in it. */
export function layerRows(p: PartPlacements | null): LayerRow[] {
  if (!p) return []
  return p.layers.map((l) => ({ id: l.id, label: l.label, count: p.placements.filter((x) => x.layer === l.id).length }))
}

/** The part ids a 3D object belongs to: the notes' model_names link first, then the model's own list. */
export function partIdsOfObject(name: string, notes: Notes | null, ring: RingModel | null): string[] {
  const out: string[] = []
  for (const [id, n] of Object.entries(notes ?? {})) if (id.startsWith('ring:') && n.model_names.includes(name)) out.push(id)
  for (const id of ring?.nodes.find((n) => n.name === name)?.part_ids ?? []) if (!out.includes(id)) out.push(id)
  return out
}

export interface ObjectRow {
  /** the 3D object's name in the model */
  name: string
  /** the part it belongs to, or null when it has no parts-list line */
  partId: string | null
  /** words for the row: the parts-list item, else the object's own name with spaces */
  label: string
  /** the reference the object belongs to (the part id after the colon), for telling equal items apart */
  ref: string | null
}

const spaced = (name: string): string => name.replace(/[_-]+/g, ' ').trim()

/** The objects of one layer, each tied to its parts-list line where there is one. */
export function objectsOfLayer(
  layer: string,
  p: PartPlacements | null,
  parts: Parts | null,
  notes: Notes | null,
  ring: RingModel | null,
): ObjectRow[] {
  return (p?.placements ?? [])
    .filter((x) => x.layer === layer)
    .map((x) => {
      const partId = partIdsOfObject(x.name, notes, ring)[0] ?? null
      const line = partId ? ringLines(parts).find((l) => l.part_ids.includes(partId)) : null
      return { name: x.name, partId, label: line?.item ?? spaced(x.name), ref: partId ? partId.slice(partId.indexOf(':') + 1) : null }
    })
}

export const lineOf = (parts: Parts | null, id: string): PartsLine | null =>
  (parts?.lines ?? []).find((l) => l.part_ids.includes(id)) ?? null

/** The layer a part sits in (through the object that carries it), or null when no object of the model carries it. */
export function layerOfPart(id: string, p: PartPlacements | null, notes: Notes | null, ring: RingModel | null): string | null {
  return p?.placements.find((x) => partIdsOfObject(x.name, notes, ring).includes(id))?.layer ?? null
}

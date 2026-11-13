// Pure helpers of the Parts screen. No ring value is written here: every word shown comes from the bundle.
import type { BannerSpec, Files, Parts, PartsLine, SchematicPages } from '../../contract'

export type Has = 'code' | 'drawing'
export interface FilterModel {
  /** one of the two exclusive choices: a maker order code exists, or the line is made to a drawing */
  has: Has | null
  /** the line carries a named open action (a question for a supplier or a maker) */
  supplier: boolean
  /** a schematic page id: only the parts that sit on that page */
  page: string | null
}
export const NO_FILTER: FilterModel = { has: null, supplier: false, page: null }
export const isFiltered = (m: FilterModel): boolean => m.has !== null || m.supplier || m.page !== null

/** URL: ?f=code,supplier&page=<id>. Unknown words are ignored; 'code' and 'drawing' never hold together. */
export function parseFilter(p: URLSearchParams): FilterModel {
  const words = (p.get('f') ?? '').split(',').map((w) => w.trim())
  const has: Has | null = words.includes('code') ? 'code' : words.includes('drawing') ? 'drawing' : null
  const page = p.get('page')
  return { has, supplier: words.includes('supplier'), page: page && page.length <= 80 ? page : null }
}

/** The address with the filter written into it; every other parameter (part) is kept. */
export function writeFilter(p: URLSearchParams, m: FilterModel): URLSearchParams {
  const next = new URLSearchParams(p)
  const words = [m.has, m.supplier ? 'supplier' : null].filter(Boolean)
  if (words.length) next.set('f', words.join(','))
  else next.delete('f')
  if (m.page) next.set('page', m.page)
  else next.delete('page')
  return next
}

const text = (s: string | null | undefined): string => (s ?? '').trim()
export const hasCode = (l: PartsLine): boolean => text(l.maker_part_number) !== ''
/** Nothing to order by code: the maker builds it to a drawing (or it is still to be named). */
export const madeToDrawing = (l: PartsLine): boolean => !hasCode(l)
export const needsSupplier = (l: PartsLine): boolean => text(l.open_action) !== ''

export function matches(l: PartsLine, m: FilterModel, pageIds: ReadonlySet<string> | null): boolean {
  if (m.has === 'code' && !hasCode(l)) return false
  if (m.has === 'drawing' && !madeToDrawing(l)) return false
  if (m.supplier && !needsSupplier(l)) return false
  if (m.page && !(pageIds && l.part_ids.some((id) => pageIds.has(id)))) return false
  return true
}

export const linesOf = (parts: Parts | null, bom: 'ring' | 'case'): PartsLine[] => (parts?.lines ?? []).filter((l) => l.bom === bom)

export const pageIdsOf = (pages: SchematicPages | null, page: string | null): ReadonlySet<string> | null => {
  if (!page) return null
  const p = pages?.pages.find((x) => x.id === page)
  return p ? new Set(p.part_ids) : new Set()
}

const plural = (n: number, one: string, many: string): string => `${n} ${n === 1 ? one : many}`
export const linesWord = (n: number): string => plural(n, 'line', 'lines')
export const partsWord = (n: number): string => plural(n, 'part', 'parts')

/** 'GBP 3.28 · USD 3.23': sums per currency, never added across currencies. */
export function pricedSum(parts: Parts, bom: 'ring' | 'case'): string {
  return parts.priced_sums
    .filter((s) => s.bom === bom)
    .map((s) => `${s.currency} ${s.amount.toFixed(2)}`)
    .join(' · ')
}

/** The line that holds this part id. */
export const lineOfPart = (parts: Parts | null, id: string): PartsLine | null => parts?.lines.find((l) => l.part_ids.includes(id)) ?? null

/** The record marks old-design lines in its manifest message: "... made for design A1; the design is now A5-draft."
 *  Returns the contract's stale banner for the lines of one bom, or null when the record says nothing. */
export function oldDesignBanner(message: string | null | undefined, bom: 'ring' | 'case'): BannerSpec | null {
  if (!message) return null
  const word = bom === 'case' ? 'case' : 'ring'
  const m = new RegExp(`${word} lines were made for design (\\S+?); the design is now (\\S+?)\\.`, 'i').exec(message)
  return m && m[1] && m[2] ? { kind: 'stale', basis: m[1], current: m[2] } : null
}

/** A file of files.json whose file name holds this part's reference as a whole word: the maker drawing. */
export function makerFiles(files: Files | null, line: PartsLine): string[] {
  if (!files) return []
  const refs = line.refs.map((r) => r.toLowerCase())
  return files.files
    .map((f) => f.path)
    .filter((p) => (p.split('/').pop() ?? p).split(/[^A-Za-z0-9]+/).some((w) => refs.includes(w.toLowerCase())))
    .slice(0, 4)
}

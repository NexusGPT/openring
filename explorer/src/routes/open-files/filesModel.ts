// Files: the area groups of files.json, and the two hand-off sets (manufacturer, 3D printer) found by
// PATH RULES over the same list. No file name of the ring is written here; a rule names a folder, an
// extension or a word of a name, and what it finds is whatever the bundle lists.
import type { AreaId, Files } from '../../contract'
import { TAB_LABEL } from '../../app/route-names'
import { baseName } from './format'

export type FileRow = Files['files'][number]
type Area = AreaId | 'other'

const AREA_ORDER: readonly Area[] = ['look', 'inside', 'electronics', 'board', 'parts', 'behaviour', 'case', 'open', 'other']
/** The folder the design lane fills with the hand-off files. */
export const MFG_DIR = 'design/mfg/'

export interface AreaGroup {
  area: Area
  label: string
  files: FileRow[]
  bytes: number
}

export const areaLabel = (a: Area): string => (a === 'other' ? 'Other' : TAB_LABEL[a])

/** One group per area that has files, in the owner's reading order; rows by path. */
export function areaGroups(files: FileRow[]): AreaGroup[] {
  const by = new Map<Area, FileRow[]>()
  for (const f of files) by.set(f.area, [...(by.get(f.area) ?? []), f])
  const known = AREA_ORDER.filter((a) => by.has(a))
  const rest = [...by.keys()].filter((a) => !AREA_ORDER.includes(a))
  return [...known, ...rest].map((area) => {
    const rows = [...(by.get(area) ?? [])].sort((a, b) => (a.path < b.path ? -1 : 1))
    return { area, label: areaLabel(area), files: rows, bytes: rows.reduce((n, f) => n + f.size_bytes, 0) }
  })
}

const ext = (p: string): string => (/\.([a-z0-9]+)$/i.exec(p)?.[1] ?? '').toLowerCase()
/** Folders of the generator's own tools and test data are not for a partner: they never enter a hand-off set. */
const NOISE = /(^|\/)(tools|testdata|tests|__pycache__|\.cache)(\/|$)/
const inMfg = (p: string): boolean => p.startsWith(MFG_DIR) && !NOISE.test(p.slice(MFG_DIR.length))

export interface Kind {
  id: string
  label: string
  /** what the owner is told is coming while the kind is empty */
  coming: string
  files: FileRow[]
}
const MFG_KINDS: readonly { id: string; label: string; coming: string; test: (f: FileRow) => boolean }[] = [
  { id: 'wiring', label: 'Wiring diagram', coming: 'wiring diagram as PDF', test: (f) => ext(f.path) === 'pdf' && /wiring/i.test(baseName(f.path)) },
  { id: 'parts-list', label: 'Parts list', coming: 'parts list', test: (f) => /(^|\/)bom\.csv$/i.test(f.path) },
  { id: 'spec', label: 'Specifications', coming: 'one-page specifications', test: (f) => inMfg(f.path) && /spec/i.test(f.path.slice(MFG_DIR.length)) },
  { id: 'drawing', label: 'Drawings (PDF)', coming: 'dimensioned drawings as PDF', test: (f) => inMfg(f.path) && ext(f.path) === 'pdf' },
  { id: 'step', label: 'CAD files (STEP)', coming: 'CAD files as STEP', test: (f) => inMfg(f.path) && ['step', 'stp'].includes(ext(f.path)) },
]

/** "For a manufacturer": each kind with the files that match it (a file counts once, first kind wins). */
export function manufacturerKinds(files: FileRow[]): Kind[] {
  const taken = new Set<string>()
  const out = MFG_KINDS.map(({ test, ...k }) => {
    const rows = files.filter((f) => !taken.has(f.path) && test(f)).sort((a, b) => (a.path < b.path ? -1 : 1))
    for (const r of rows) taken.add(r.path)
    return { ...k, files: rows }
  })
  const other = files.filter((f) => inMfg(f.path) && ext(f.path) !== 'stl' && !taken.has(f.path))
  return other.length ? [...out, { id: 'other', label: 'More files', coming: '', files: other }] : out
}

export interface PrintPart {
  key: string
  label: string
  /** rows of one part; `size` is the ring size when the file name carries one */
  files: { file: FileRow; size: string | null }[]
}
const SIZE_RE = /[-_ ]?size[-_ ]?(\d+(?:\.\d+)?)/i

/** "For a 3D printer": every .stl under the mfg folder, grouped by part, sized files by ring size. */
export function printParts(files: FileRow[]): PrintPart[] {
  const parts = new Map<string, PrintPart>()
  for (const f of files.filter((x) => inMfg(x.path) && ext(x.path) === 'stl')) {
    const stem = baseName(f.path).replace(/\.stl$/i, '')
    const size = SIZE_RE.exec(stem)?.[1] ?? null
    const key = stem.replace(SIZE_RE, '') || stem
    const p = parts.get(key) ?? { key, label: key.replace(/[-_]+/g, ' ').trim(), files: [] }
    p.files.push({ file: f, size })
    parts.set(key, p)
  }
  const num = (s: string | null): number => (s === null ? -1 : Number(s))
  return [...parts.values()]
    .map((p) => ({ ...p, files: p.files.sort((a, b) => num(a.size) - num(b.size) || (a.file.path < b.file.path ? -1 : 1)) }))
    .sort((a, b) => (a.label < b.label ? -1 : 1))
}

/** Rows of a file list that match a typed word (path, case-insensitive); an empty word keeps all. */
export const matching = (files: FileRow[], q: string): FileRow[] => {
  const w = q.trim().toLowerCase()
  return w ? files.filter((f) => f.path.toLowerCase().includes(w)) : files
}

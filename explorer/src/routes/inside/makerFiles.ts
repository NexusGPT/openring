// Maker files of one part, found in the bundle's `files` record. Nothing is typed per part: a file belongs to
// a part when a word of its path (under the maker-files folder) is one of the part's references, and its kind
// comes from its extension and from the words front / side / top / spec / size N in the path.
import type { Files, PartsLine } from '../../contract'

/** Where the maker files of the design live, as a folder in the repository. */
export const MFG_ROOT = 'design/mfg/'
export type FileKind = 'drawing' | 'spec' | 'step' | 'stl'
export type ViewName = 'front' | 'side' | 'top'
export const VIEW_NAMES: readonly ViewName[] = ['front', 'side', 'top']
export const FILE_LABEL: Record<FileKind, string> = { drawing: 'Drawing PDF', spec: 'Specification', step: 'STEP', stl: 'STL' }
export const FILE_KINDS: readonly FileKind[] = ['drawing', 'spec', 'step', 'stl']

/** Ring size shown first when a part has files per size. */
export const DEFAULT_RING_SIZE = 9

/** A file of the record, with the optional fields the files reader adds for maker files. */
type RecFile = Files['files'][number] & { part_ids?: string[]; kind?: string; ring_size?: number | null }

export interface MakerFile {
  path: string
  /** 'sheet' = one drawing picture holding all the views */
  kind: FileKind | 'view' | 'sheet'
  view: ViewName | null
  /** ring size the file is for; null = every size */
  size: number | null
}
export interface MakerSet {
  files: MakerFile[]
  /** ring sizes that have their own files, ascending */
  sizes: number[]
}

const words = (rest: string): string[] => rest.toLowerCase().replace(/\.[a-z0-9]+$/, '').split(/[^a-z0-9]+/).filter(Boolean)
const extOf = (p: string): string => (/\.([A-Za-z0-9]+)$/.exec(p)?.[1] ?? '').toLowerCase()

function sizeOf(w: string[]): number | null {
  for (let i = 0; i < w.length; i++) {
    const t = w[i] ?? ''
    const joined = /^(?:size|us)(\d+)$/.exec(t)
    if (joined) return Number(joined[1])
    if ((t === 'size' || t === 'us') && /^\d+$/.test(w[i + 1] ?? '')) return Number(w[i + 1])
  }
  return null
}

function kindOf(ext: string, w: string[]): { kind: MakerFile['kind']; view: ViewName | null } | null {
  const view = VIEW_NAMES.find((v) => w.includes(v)) ?? null
  const spec = w.includes('spec') || w.includes('specification')
  if (ext === 'svg') return view ? { kind: 'view', view } : { kind: 'sheet', view: null }
  if (ext === 'pdf') return { kind: spec ? 'spec' : 'drawing', view: null }
  if (ext === 'step' || ext === 'stp') return { kind: 'step', view: null }
  if (ext === 'stl') return { kind: 'stl', view: null }
  if (spec && (ext === 'md' || ext === 'txt' || ext === 'html')) return { kind: 'spec', view: null }
  return null
}

/** The maker files of a parts-list line (its references name them). */
export function makerFiles(files: Files | null, line: PartsLine | null): MakerSet {
  if (!files || !line) return { files: [], sizes: [] }
  const refs = new Set(line.refs.map((r) => r.toLowerCase()))
  const ids = new Set(line.part_ids)
  const out: MakerFile[] = []
  for (const f of files.files as RecFile[]) {
    if (f.part_ids) {
      // the files reader says which parts the file is for, its kind and its ring size
      if (!f.part_ids.some((id) => ids.has(id))) continue
      const w = words(f.path.slice(f.path.startsWith(MFG_ROOT) ? MFG_ROOT.length : 0))
      const ext = extOf(f.path)
      const k: MakerFile['kind'] | null =
        f.kind === 'specification' ? 'spec' : f.kind === 'drawing' || f.kind === 'step' || f.kind === 'stl' ? f.kind : f.kind === 'view' ? (ext === 'svg' ? (VIEW_NAMES.some((v) => w.includes(v)) ? 'view' : 'sheet') : null) : null
      if (k) out.push({ path: f.path, kind: k, view: k === 'view' ? (VIEW_NAMES.find((v) => w.includes(v)) ?? null) : null, size: f.ring_size ?? null })
      continue
    }
    if (!f.path.startsWith(MFG_ROOT)) continue
    const w = words(f.path.slice(MFG_ROOT.length))
    if (!w.some((t) => refs.has(t))) continue
    const k = kindOf(extOf(f.path), w)
    if (k) out.push({ path: f.path, kind: k.kind, view: k.view, size: sizeOf(w) })
  }
  const sizes = [...new Set(out.flatMap((f) => (f.size === null ? [] : [f.size])))].sort((a, b) => a - b)
  return { files: out, sizes }
}

const forSize = (f: MakerFile, size: number | null): boolean => f.size === null || size === null || f.size === size

/** The file to give for one button at one ring size, or null when it is not made yet. */
export function fileFor(set: MakerSet, kind: FileKind, size: number | null): MakerFile | null {
  const c = set.files.filter((f) => f.kind === kind && forSize(f, size))
  return c.find((f) => f.size === size && size !== null) ?? c[0] ?? null
}

/** The one sheet holding all the views of a part at one ring size, or null. */
export function sheetFor(set: MakerSet, size: number | null): MakerFile | null {
  const c = set.files.filter((f) => f.kind === 'sheet' && forSize(f, size))
  return c.find((f) => f.size === size && size !== null) ?? c[0] ?? null
}

/** Ring size chosen first: the default when the part has it, else the smallest. */
export const firstSize = (set: MakerSet): number | null => (set.sizes.includes(DEFAULT_RING_SIZE) ? DEFAULT_RING_SIZE : (set.sizes[0] ?? null))

/** The flat view of one name at one ring size, or null when it is not drawn yet. */
export function viewFor(set: MakerSet, view: ViewName, size: number | null): MakerFile | null {
  const c = set.files.filter((f) => f.kind === 'view' && f.view === view && forSize(f, size))
  return c.find((f) => f.size === size && size !== null) ?? c[0] ?? null
}

/** A part is made to drawing when its line names no maker and no order code, and its open action asks for a drawing or an outline. */
export function isMadeToDrawing(line: PartsLine | null): boolean {
  if (!line || line.maker_part_number || line.maker) return false
  return /\b(drawing|outline)\b/i.test(line.open_action ?? '')
}

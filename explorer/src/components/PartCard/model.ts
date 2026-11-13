// Pure helpers for the part card: what to show, which links work. No ring value is written here.
import type { AreaState, Files, Parts, PartsLine } from '../../contract'
import { WORDS } from '../../contract'
import { fileUrl } from '../../data'

export type Legend = Parts['evidence_legend']

/** The plain meaning of an evidence code, from the bundle's own legend. */
export function evidenceMeaning(code: PartsLine['evidence'], legend: Legend | null): string | null {
  if (!code) return null
  return legend?.find((l) => l.code === code)?.meaning ?? code
}

/** Accent is for attention only: a line that waits on a supplier, or carries an open action. */
export function needsAttention(line: PartsLine | null, areaState: AreaState | null | undefined): boolean {
  return areaState === 'waiting on a supplier' || Boolean(line?.open_action)
}

export interface CardLink {
  key: string
  label: string
  /** null = the file is not on disk: render greyed, aria-disabled */
  href: string | null
  external: boolean
}

const baseName = (p: string): string => p.split('/').filter(Boolean).pop() ?? p
const isHttp = (u: string): boolean => /^https?:\/\//i.test(u)

/** Every source of a line as a link. A path is linked only when the file is flagged on disk and, when the
 *  file list is known, listed in it (the server answers only for listed files). */
export function sourceLinks(line: PartsLine, files: Files | null): CardLink[] {
  const allowed = files ? new Set(files.files.map((f) => f.path)) : null
  const out: CardLink[] = []
  const seen = new Set<string>()
  const add = (l: CardLink) => {
    if (!seen.has(l.key)) {
      seen.add(l.key)
      out.push(l)
    }
  }
  add({
    key: `row:${line.source.file}`,
    label: `${baseName(line.source.file)}, row ${line.row}`,
    href: allowed?.has(line.source.file) ? fileUrl(line.source.file) : null,
    external: false,
  })
  for (const s of line.sources) {
    if (s.path) {
      const ok = s.on_disk && (allowed ? allowed.has(s.path) : true)
      add({ key: `p:${s.path}`, label: baseName(s.path), href: ok ? fileUrl(s.path) : null, external: false })
    } else if (s.url && isHttp(s.url)) {
      add({ key: `u:${s.url}`, label: s.raw || s.url, href: s.url, external: true })
    } else {
      add({ key: `r:${s.raw}`, label: s.raw, href: null, external: false })
    }
  }
  return out
}

export const NOT_ON_DISK = WORDS.notOnDisk
export const NO_LINE = WORDS.noPartsLine

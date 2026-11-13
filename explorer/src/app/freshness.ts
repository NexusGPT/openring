// The freshness stamp: when the data bundle was built and from which commit. Pure; no clock is read.
import type { Manifest } from '../contract'

export interface Stamp {
  text: string
  dirty: boolean
}

/** 'Data built <date time> · commit <7 chars>', plus ' · files changed since' when the design had
 *  uncommitted changes. The date is manifest.built_at in the browser's locale. */
export function stampOf(m: Pick<Manifest, 'built_at' | 'git_commit' | 'git_dirty'>, locale?: string | string[]): Stamp {
  const built = new Date(m.built_at)
  const when = Number.isNaN(built.getTime()) ? m.built_at : built.toLocaleString(locale)
  const text = `Data built ${when} · commit ${m.git_commit.slice(0, 7)}`
  return { text: m.git_dirty ? `${text} · files changed since` : text, dirty: m.git_dirty }
}

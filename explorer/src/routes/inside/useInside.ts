// Everything the Inside screen reads, with the honest state of each record turned into banners.
import { useMemo } from 'react'
import { usePartNotes, useRecord } from '../../data'
import type { BannerSpec } from '../../contract'

const NAMES = ['ring-model.json', 'placements.json', 'parts.json', 'files.json', 'areas.json', 'content/part-notes.json'] as const

export function useInside() {
  const ring = useRecord('ring-model')
  const placements = useRecord('part-placements')
  const parts = useRecord('parts')
  const files = useRecord('files')
  const areas = useRecord('area-states')
  const notes = usePartNotes()
  const all = [ring, placements, parts, files, areas, notes]
  const loading = all.some((r) => r.loading)

  const banners = useMemo<BannerSpec[]>(() => {
    const out: BannerSpec[] = []
    const add = (b: BannerSpec) => {
      if (!out.some((o) => JSON.stringify(o) === JSON.stringify(b))) out.push(b)
    }
    all.forEach((r, i) => {
      const s = r.state
      if (!s) return
      const file = NAMES[i] ?? ''
      if (s.status === 'missing') add({ kind: 'missing' })
      else if (s.status === 'unparsed') add({ kind: 'unparsed', file: s.entry.source[0] ?? file })
      else if (s.status === 'stale') add({ kind: 'stale', basis: s.entry.basis_version ?? '?', current: s.entry.current_version ?? '?' })
    })
    return out
  }, [ring.state, placements.state, parts.state, files.state, areas.state, notes.state])

  const stale = all.some((r) => r.state?.status === 'stale')
  return {
    loading,
    banners,
    stale,
    ringModel: ring.state?.data ?? null,
    placements: placements.state?.data ?? null,
    parts: parts.state?.data ?? null,
    files: files.state?.data ?? null,
    version: areas.state?.data?.design_version ?? null,
    updated: areas.state?.data?.updated ?? null,
    insideArea: areas.state?.data?.areas.find((a) => a.id === 'inside') ?? null,
    notes: notes.state?.data?.notes ?? null,
  }
}

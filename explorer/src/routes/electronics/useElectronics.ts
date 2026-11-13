// Everything the Electronics screen reads, each record with its honest state turned into banners.
import { useMemo } from 'react'
import { usePartNotes, useRecord } from '../../data'
import type { BannerSpec } from '../../contract'

const FILE = ['electronics.json', 'schematic/index.json', 'parts.json'] as const

export function useElectronics() {
  const el = useRecord('electronics')
  const pages = useRecord('schematic-pages')
  const parts = useRecord('parts')
  const files = useRecord('files')
  const boards = useRecord('board-files')
  const areas = useRecord('area-states')
  const notes = usePartNotes()
  const shown = [el, pages, parts]
  const loading = [...shown, files, areas, notes, boards].some((r) => r.loading)

  const banners = useMemo<BannerSpec[]>(() => {
    const out: BannerSpec[] = []
    const add = (b: BannerSpec) => {
      if (!out.some((o) => JSON.stringify(o) === JSON.stringify(b))) out.push(b)
    }
    shown.forEach((r, i) => {
      const s = r.state
      if (!s) return
      if (s.status === 'missing') add({ kind: 'missing' })
      else if (s.status === 'unparsed') add({ kind: 'unparsed', file: s.entry.source[0] ?? FILE[i] ?? '' })
      else if (s.status === 'stale') add({ kind: 'stale', basis: s.entry.basis_version ?? '?', current: s.entry.current_version ?? '?' })
    })
    return out
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [el.state, pages.state, parts.state])

  return {
    loading,
    banners,
    stale: shown.some((r) => r.state?.status === 'stale'),
    electronics: el.state?.data ?? null,
    pages: pages.state?.data ?? null,
    parts: parts.state?.data ?? null,
    files: files.state?.data ?? null,
    /** the groups of boards the Board screen shows: a connection end opens one of them */
    boardGroups: [...new Set((boards.state?.data?.boards ?? []).map((b) => b.group))],
    notes: notes.state?.data?.notes ?? null,
    area: areas.state?.data?.areas.find((a) => a.id === 'electronics') ?? null,
    version: areas.state?.data?.design_version ?? null,
    updated: areas.state?.data?.updated ?? null,
  }
}

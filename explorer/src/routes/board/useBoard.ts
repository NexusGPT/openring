// Everything the Board screen reads, each record with its honest state.
import { useMemo } from 'react'
import { usePartNotes, useRecord } from '../../data'
import type { BannerSpec } from '../../contract'

export function useBoard() {
  const board = useRecord('board-files')
  const parts = useRecord('parts')
  const placements = useRecord('part-placements')
  const files = useRecord('files')
  const electronics = useRecord('electronics')
  const areas = useRecord('area-states')
  const notes = usePartNotes()
  const shown = [board, parts, placements]
  const loading = [...shown, files, areas, notes, electronics].some((r) => r.loading)

  const banners = useMemo<BannerSpec[]>(() => {
    const out: BannerSpec[] = []
    const add = (b: BannerSpec) => {
      if (!out.some((o) => JSON.stringify(o) === JSON.stringify(b))) out.push(b)
    }
    const names = ['board/index.json', 'parts.json', 'placements.json']
    shown.forEach((r, i) => {
      const s = r.state
      if (!s) return
      if (s.status === 'missing') add({ kind: 'missing' })
      else if (s.status === 'unparsed') add({ kind: 'unparsed', file: s.entry.source[0] ?? names[i] ?? '' })
      else if (s.status === 'stale') add({ kind: 'stale', basis: s.entry.basis_version ?? '?', current: s.entry.current_version ?? '?' })
    })
    // a record with the list of boards says each board's state itself (its rules check); the older single-board note stays for data without the list
    const b = board.state?.data
    if (b && !b.boards && !b.routed) add({ kind: 'board-not-routed', missing: b.missing })
    return out
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [board.state, parts.state, placements.state])

  return {
    loading,
    banners,
    stale: shown.some((r) => r.state?.status === 'stale'),
    board: board.state?.data ?? null,
    parts: parts.state?.data ?? null,
    placements: placements.state?.data ?? null,
    files: files.state?.data ?? null,
    connections: electronics.state?.data?.connection_map ?? null,
    notes: notes.state?.data?.notes ?? null,
    area: areas.state?.data?.areas.find((a) => a.id === 'board') ?? null,
    version: areas.state?.data?.design_version ?? null,
    updated: areas.state?.data?.updated ?? null,
  }
}

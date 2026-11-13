// Everything the Parts screen reads, each record with its honest state.
import { usePartNotes, useRecord } from '../../data'

export function useParts() {
  const parts = useRecord('parts')
  const files = useRecord('files')
  const areas = useRecord('area-states')
  const pages = useRecord('schematic-pages')
  const notes = usePartNotes()
  return {
    loading: parts.loading || files.loading || areas.loading || notes.loading,
    partsState: parts.state,
    parts: parts.state?.data ?? null,
    files: files.state?.data ?? null,
    pages: pages.state?.data ?? null,
    notes: notes.state?.data?.notes ?? null,
    area: areas.state?.data?.areas.find((a) => a.id === 'parts') ?? null,
    version: areas.state?.data?.design_version ?? null,
    updated: areas.state?.data?.updated ?? null,
  }
}

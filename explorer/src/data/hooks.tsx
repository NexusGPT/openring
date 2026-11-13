import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import type { RecordId, RecordTypes } from '../contract/registry'
import type { PartNotes } from '../contract/records'
import { loadManifest, loadPartNotes, loadRecord, type RecordState } from './records'

/** One cache entry per record; the bundle never changes while the app is open. */
export function createQueryClient(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { staleTime: Infinity, gcTime: Infinity, retry: false, refetchOnWindowFocus: false } } })
}

export function DataProvider({ client, children }: { client: QueryClient; children: ReactNode }) {
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

export function useManifest() {
  return useQuery({ queryKey: ['manifest'], queryFn: loadManifest })
}

/** A record with its honest state. `loading` is true only before the first answer. */
export function useRecord<K extends RecordId>(id: K): { loading: boolean; state: RecordState<RecordTypes[K]> | null } {
  const manifest = useManifest()
  const q = useQuery({
    queryKey: ['record', id],
    queryFn: () => loadRecord(id, manifest.data ?? null),
    enabled: !manifest.isPending,
  })
  return { loading: manifest.isPending || q.isPending, state: q.data ?? null }
}

/** The part notes with their honest state (same shape as useRecord). */
export function usePartNotes(): { loading: boolean; state: RecordState<PartNotes> | null } {
  const manifest = useManifest()
  const q = useQuery({
    queryKey: ['content', 'part-notes'],
    queryFn: () => loadPartNotes(manifest.data ?? null),
    enabled: !manifest.isPending,
  })
  return { loading: manifest.isPending || q.isPending, state: q.data ?? null }
}

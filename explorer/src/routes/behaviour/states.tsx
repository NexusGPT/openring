// One honest banner for a record that is not ok, in the words of the contract (route = behaviour).
import { RECORD_FILE, StateBanner, type BannerSpec, type RecordId } from '../../contract'
import type { RecordState } from '../../data'

export function specFor(id: RecordId, s: RecordState<unknown> | null): BannerSpec | null {
  if (!s) return null
  if (s.status === 'missing') return { kind: 'missing' }
  if (s.status === 'unparsed') return { kind: 'unparsed', file: s.entry.source[0] ?? RECORD_FILE[id] }
  if (s.status === 'stale') return { kind: 'stale', basis: s.entry.basis_version ?? '', current: s.entry.current_version ?? '' }
  return null
}

export function Banner({ id, state }: { id: RecordId; state: RecordState<unknown> | null }) {
  const spec = specFor(id, state)
  return spec ? <StateBanner route="behaviour" spec={spec} /> : null
}

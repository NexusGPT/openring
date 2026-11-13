// Loading the bundle. Every record resolves to one of four honest states and is never blank:
//   ok       the file is there and valid
//   stale    the file is there and valid but was made for an older design: show it, dimmed, with a banner
//   missing  no extractor ran, or the file is not in the bundle
//   unparsed the source changed and cannot be read, or the file breaks its schema
import { RECORD_FILE, RECORD_SCHEMA, RECORD_IDS, type RecordId, type RecordTypes } from '../contract/registry'
import type { Manifest, ManifestEntry, PartNotes } from '../contract/records'
import { dataUrl } from './urls'
import { schemaProblems } from './validate'

export type RecordState<T> =
  | { status: 'ok' | 'stale'; data: T; entry: ManifestEntry }
  | { status: 'missing' | 'unparsed'; data: null; entry: ManifestEntry }

const entryOf = (status: ManifestEntry['status'], message: string | null): ManifestEntry => ({
  status,
  source: [],
  basis_version: null,
  current_version: null,
  message,
})

async function getJson(url: string): Promise<{ kind: 'ok'; json: unknown } | { kind: 'absent' } | { kind: 'broken'; message: string }> {
  let res: Response
  try {
    res = await fetch(url)
  } catch (e) {
    return { kind: 'absent' }
  }
  if (res.status === 404) return { kind: 'absent' }
  if (!res.ok) return { kind: 'broken', message: `HTTP ${res.status}` }
  try {
    return { kind: 'ok', json: await res.json() }
  } catch (e) {
    return { kind: 'broken', message: 'not valid JSON' }
  }
}

/** The manifest, or null when there is none (an empty bundle: every record then reads 'missing'). */
export async function loadManifest(): Promise<Manifest | null> {
  const r = await getJson(dataUrl('manifest.json'))
  if (r.kind !== 'ok') return null
  return schemaProblems('manifest', r.json).length === 0 ? (r.json as Manifest) : null
}

export async function loadRecord<K extends RecordId>(id: K, manifest: Manifest | null): Promise<RecordState<RecordTypes[K]>> {
  const entry = manifest?.records[id] ?? entryOf('missing', null)
  if (entry.status === 'missing' || entry.status === 'unparsed') return { status: entry.status, data: null, entry }
  const r = await getJson(dataUrl(RECORD_FILE[id]))
  if (r.kind === 'absent') return { status: 'missing', data: null, entry: { ...entry, status: 'missing' } }
  if (r.kind === 'broken') return { status: 'unparsed', data: null, entry: { ...entry, status: 'unparsed', message: r.message, source: [RECORD_FILE[id]] } }
  const problems = schemaProblems(RECORD_SCHEMA[id], r.json)
  if (problems.length) {
    return {
      status: 'unparsed',
      data: null,
      entry: { ...entry, status: 'unparsed', message: problems[0] ?? 'invalid', source: [RECORD_FILE[id]] },
    }
  }
  return { status: entry.status, data: r.json as RecordTypes[K], entry }
}

export { RECORD_IDS }

/** The hand-written part notes. The collector copies content/part-notes.json into the bundle, so one URL,
 *  dataUrl('content/part-notes.json'), works in dev, preview and the static build. */
export const PART_NOTES_FILE = 'content/part-notes.json'

export async function loadPartNotes(manifest: Manifest | null): Promise<RecordState<PartNotes>> {
  const entry = manifest?.content?.['part-notes'] ?? entryOf('missing', null)
  if (entry.status === 'missing' || entry.status === 'unparsed') return { status: entry.status, data: null, entry }
  const r = await getJson(dataUrl(PART_NOTES_FILE))
  if (r.kind === 'absent') return { status: 'missing', data: null, entry: { ...entry, status: 'missing' } }
  const fail = (message: string): RecordState<PartNotes> => ({
    status: 'unparsed',
    data: null,
    entry: { ...entry, status: 'unparsed', message, source: [PART_NOTES_FILE] },
  })
  if (r.kind === 'broken') return fail(r.message)
  const problems = schemaProblems('content/part-notes', r.json)
  if (problems.length) return fail(problems[0] ?? 'invalid')
  return { status: entry.status, data: r.json as PartNotes, entry }
}

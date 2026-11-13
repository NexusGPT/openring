import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { RECORD_FILE, RECORD_IDS, type RecordId } from '../contract/registry'
import { loadManifest, loadPartNotes, loadRecord } from './records'
import { schemaProblems } from './validate'

const SAMPLE = join(__dirname, '..', '..', 'tests', 'support', 'sample-bundle')
const sample = (rel: string): unknown => JSON.parse(readFileSync(join(SAMPLE, rel), 'utf8'))

function serve(files: Record<string, unknown | 'broken'>) {
  vi.stubGlobal('fetch', async (url: string) => {
    const key = url.replace(/^\/data\//, '')
    if (!(key in files)) return new Response('no', { status: 404 })
    const v = files[key]
    return new Response(v === 'broken' ? '{nope' : JSON.stringify(v), { status: 200 })
  })
}
afterEach(() => vi.unstubAllGlobals())

describe('schemas in the browser', () => {
  it('accept the sample record of every id', () => {
    for (const id of RECORD_IDS) expect(schemaProblems(id, sample(RECORD_FILE[id]))).toEqual([])
    expect(schemaProblems('manifest', sample('manifest.json'))).toEqual([])
    expect(schemaProblems('content/part-notes', sample('content/part-notes.json'))).toEqual([])
  })
  it('refuse a parts line without refs', () => {
    const parts = sample('parts.json') as { lines: Record<string, unknown>[] }
    delete parts.lines[0]!.refs
    expect(schemaProblems('parts', parts).length).toBeGreaterThan(0)
  })
})

describe('loading a record', () => {
  it('reads every record as missing when there is no manifest', async () => {
    serve({})
    const m = await loadManifest()
    expect(m).toBeNull()
    for (const id of RECORD_IDS) {
      const s = await loadRecord(id, m)
      expect(s.status).toBe('missing')
      expect(s.data).toBeNull()
    }
  })
  it('returns the data of an ok record', async () => {
    serve({ 'manifest.json': sample('manifest.json'), 'parts.json': sample('parts.json') })
    const m = await loadManifest()
    const s = await loadRecord('parts', m)
    expect(s.status).toBe('ok')
    expect(s.data?.totals.ring.lines).toBe(2)
  })
  it('keeps the data of a stale record', async () => {
    serve({ 'manifest.json': sample('manifest.json'), 'areas.json': sample('areas.json') })
    const s = await loadRecord('area-states', await loadManifest())
    expect(s.status).toBe('stale')
    expect(s.data?.areas).toHaveLength(8)
  })
  it('says unparsed when the file breaks its schema, with the reason', async () => {
    const bad = sample('parts.json') as { lines: Record<string, unknown>[] }
    delete bad.lines[0]!.refs
    serve({ 'manifest.json': sample('manifest.json'), 'parts.json': bad })
    const s = await loadRecord('parts', await loadManifest())
    expect(s.status).toBe('unparsed')
    expect(s.entry.message).toContain('refs')
  })
  it('says unparsed on invalid JSON and missing when the manifest says ok but the file is gone', async () => {
    serve({ 'manifest.json': sample('manifest.json'), 'parts.json': 'broken' })
    const m = await loadManifest()
    expect((await loadRecord('parts', m)).status).toBe('unparsed')
    expect((await loadRecord('files' as RecordId, m)).status).toBe('missing')
  })
})

describe('loading the part notes', () => {
  it('reads them from the bundle under content/', async () => {
    serve({ 'manifest.json': sample('manifest.json'), 'content/part-notes.json': sample('content/part-notes.json') })
    const s = await loadPartNotes(await loadManifest())
    expect(s.status).toBe('ok')
    expect(Object.keys(s.data?.notes ?? {})).toEqual(['ring:ZZ9'])
  })
  it('says missing with no manifest and unparsed on a broken file', async () => {
    serve({})
    expect((await loadPartNotes(await loadManifest())).status).toBe('missing')
    serve({ 'manifest.json': sample('manifest.json'), 'content/part-notes.json': { notes: { 'ring:ZZ9': { what: 'x' } } } })
    expect((await loadPartNotes(await loadManifest())).status).toBe('unparsed')
  })
})

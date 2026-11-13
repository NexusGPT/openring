// Test bundles for the Look checks: a copy of the live bundle (public/data) with a looks/ record written here,
// plus a source folder holding the models, so the stage loads real GLBs. Made-up option texts; real finish colours.
import { copyFileSync, cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import type { LookOptions, RingModel } from '../../../src/contract/records'
import { EXPLORER_ROOT } from '../../support'

export const LIVE = join(EXPLORER_ROOT, 'public', 'data')
export const ringOf = (dir: string): RingModel => JSON.parse(readFileSync(join(dir, 'ring-model.json'), 'utf8')) as RingModel

export const FINISHES = [
  { name: 'Black finish', colour: '#14151a', roughness: 0.24 },
  { name: 'Titanium finish', colour: '#5a5f66', roughness: 0.3 },
  { name: 'Silver finish', colour: '#cfd2d6', roughness: 0.22 },
  { name: 'Gold finish', colour: '#c99a52', roughness: 0.24 },
]
const src = { file: 'design/look/test/notes.md', line: 1 }

export interface OptionSpec {
  id: string
  title: string
  rejected?: boolean
  in_design?: boolean
  glb?: boolean
}
export const SIX: OptionSpec[] = [
  { id: 'a', title: 'Look A: MONOLITH' },
  { id: 'b', title: 'Look B: SIGNET' },
  { id: 'c', title: 'Look C: CAPSULE' },
]

export interface Made {
  dir: string
  source: string
  looks: LookOptions
  cleanup(): void
}

/** copy of the live bundle with `looks/index.json`; `picked` and the option list are the case. */
export function makeBundle(options: OptionSpec[] | null, picked: string | null = null): Made {
  // options === null: the look-options record is absent (manifest says missing), as before the collector landed it
  const root = mkdtempSync(join(tmpdir(), 'look-check-'))
  const dir = join(root, 'data')
  const source = join(root, 'src')
  cpSync(LIVE, dir, { recursive: true, filter: (p) => !p.endsWith('bundle.zip') })
  mkdirSync(join(source, 'looks'), { recursive: true })
  const files = JSON.parse(readFileSync(join(dir, 'files.json'), 'utf8')) as { files: { path: string; size_bytes?: number }[] }
  const ring = ringOf(dir)
  const looks: LookOptions = {
    picked,
    finishes: FINISHES.map((f) => ({ ...f, source: src })),
    options: (options ?? []).map((o) => {
      const rel = `looks/${o.id}.glb`
      if (o.glb !== false) {
        copyFileSync(join(dir, ring.exterior.file ?? 'exterior.glb'), join(source, rel))
        files.files.push({ path: rel, size_bytes: 1 })
      }
      return {
        id: o.id,
        title: o.title,
        sentence: `Made-up sentence for ${o.title}.`,
        worse_at: ['made-up trade-off one', 'made-up trade-off two'],
        glb: o.glb === false ? null : { file: rel, size_bytes: 1, bounds_mm: { x: 30, y: 20, z: 10 } },
        rejected: !!o.rejected,
        in_design: !!o.in_design,
        source: src,
      }
    }),
  }
  rmSync(join(dir, 'looks'), { recursive: true, force: true })
  if (options) {
    mkdirSync(join(dir, 'looks'), { recursive: true })
    writeFileSync(join(dir, 'looks', 'index.json'), JSON.stringify(looks))
  }
  writeFileSync(join(dir, 'files.json'), JSON.stringify(files))
  const m = JSON.parse(readFileSync(join(dir, 'manifest.json'), 'utf8')) as { records: Record<string, unknown> }
  m.records['look-options'] = options
    ? { status: 'ok', source: ['looks/index.json'], basis_version: null, current_version: null, message: '' }
    : { status: 'missing', source: [], basis_version: null, current_version: null, message: 'No extractor for this record yet.' }
  writeFileSync(join(dir, 'manifest.json'), JSON.stringify(m))
  return { dir, source, looks, cleanup: () => rmSync(root, { recursive: true, force: true }) }
}

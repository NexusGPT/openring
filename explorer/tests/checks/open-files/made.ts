// Made-up bundles for the open-files checks: made-up words, real structure. Nothing here is a ring fact.
// `made` has 7 supplier requests, files in every area, the hand-off folder filled, and a partner zip.
// `bare` has 0 supplier requests, no zip, and an empty hand-off folder.
import { cpSync, mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { EXPLORER_ROOT, SAMPLE_BUNDLE } from '../../support'

const AREAS = ['look', 'inside', 'electronics', 'board', 'parts', 'behaviour', 'case', 'open', 'other'] as const
const src = { file: 'zz/notes.md', line: 3 }
const sizes = [5, 6, 7, 8, 9, 10, 11, 12, 13]

interface Made {
  data: string
  source: string
  /** repo-relative path -> bytes */
  disk: Map<string, Buffer>
  files: { path: string; size_bytes: number; modified: string; area: string; tracked: boolean }[]
  bundle: { file: string; size_bytes: number; contents: string[] } | null
  open: unknown
}

function filesFor(withMfg: boolean): Map<string, Buffer> {
  const disk = new Map<string, Buffer>()
  AREAS.forEach((a, i) => {
    for (let n = 0; n < 2 + (i % 3); n++) disk.set(`zz/${a}/file-${n}.txt`, Buffer.from(`made-up ${a} ${n}`.repeat(5 + n)))
  })
  disk.set('zz/parts/Pin D+.step', Buffer.from('plus sign in the name'))
  disk.set('zz/notes.md', Buffer.from('notes'))
  disk.set('zz/zz-bom.csv', Buffer.from('a,b\n1,2\n'))
  if (withMfg) {
    disk.set('design/mfg/body-drawing.pdf', Buffer.from('%PDF drawing'))
    disk.set('design/mfg/specs/body.md', Buffer.from('spec in a specs folder'))
    disk.set('design/mfg/body.step', Buffer.from('STEP body'))
    disk.set('design/mfg/zz-wiring.pdf', Buffer.from('%PDF wiring'))
    disk.set('design/bom.csv', Buffer.from('ref,qty\nZ1,1\n'))
    for (const s of sizes) disk.set(`design/mfg/stl/body-size${s}.stl`, Buffer.from(`solid body ${s}`))
    disk.set('design/mfg/stl/zz-lid.stl', Buffer.from('solid lid'))
    // the generator's own test data sits under the same folder and must never reach a hand-off set
    disk.set('design/mfg/tools/testdata/zz-bad.step', Buffer.from('bad'))
    disk.set('design/mfg/tools/zz-gen.stl', Buffer.from('solid gen'))
  }
  return disk
}

export function makeBundle(kind: 'made' | 'bare'): Made {
  const root = mkdtempSync(join(tmpdir(), `open-files-${kind}-`))
  const data = join(root, 'data')
  const source = join(root, 'src')
  cpSync(SAMPLE_BUNDLE, data, { recursive: true })
  // the stage asks for the model files: borrow the live ones so no check sees a 404 that is not about this screen
  for (const m of ['exterior.glb', 'internals.glb']) {
    const live = join(EXPLORER_ROOT, 'public', 'data', m)
    if (existsSync(live)) cpSync(live, join(data, m))
  }
  const disk = filesFor(kind === 'made')
  const files = [...disk.entries()].map(([path, b], i) => {
    const area = path.startsWith('design/mfg/') ? 'inside' : path === 'design/bom.csv' ? 'parts' : (AREAS.find((a) => path.startsWith(`zz/${a}/`)) ?? 'other')
    return { path, size_bytes: b.length, modified: `2026-11-0${1 + (i % 9)}T10:00:00Z`, area, tracked: true }
  })
  for (const [p, b] of disk) {
    mkdirSync(dirname(join(source, p)), { recursive: true })
    writeFileSync(join(source, p), b)
  }
  const bundle = kind === 'made' ? { file: 'bundle.zip', size_bytes: 0, contents: files.map((f) => f.path) } : null
  if (bundle) {
    const bytes = Buffer.concat([Buffer.from('PK'), Buffer.alloc(3000, 7)])
    writeFileSync(join(data, 'bundle.zip'), bytes)
    bundle.size_bytes = bytes.length
  }
  const supplier = kind === 'made' ? 7 : 0
  const open = {
    supplier_requests: Array.from({ length: supplier }, (_, i) => ({ id: `ZS${i}`, item: `made-up item ${i}`, who: `zz-supplier-${i % 3}`, ask: `made-up question ${i}`, section: 'zz', source: src })),
    bench_tests: [{ id: 'ZB1', title: 'made-up test', detail: null, source: src }, { id: 'ZB2', title: 'made-up test two', detail: 'made-up detail', source: src }],
    risks: [{ id: 'ZR1', text: 'made-up risk', source: src }],
    decisions: ['2026-02-01', '2026-05-09', '2026-03-15', '2026-05-02'].map((date, i) => ({ date, speaker: 'owner', quote: `made-up quote ${i}`, source: src })),
  }
  writeFileSync(join(data, 'open.json'), JSON.stringify(open))
  writeFileSync(join(data, 'files.json'), JSON.stringify({ files, bundle }))
  return { data, source, disk, files, bundle, open }
}

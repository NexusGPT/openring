// A made-up bundle for the Electronics and Board checks: the sample bundle plus 7 blocks, 8 schematic pages
// with real SVG files, a pin plan, a power budget, and a board plan with parts on both sides.
// Every value is invented (refs ZQ1..); none is a ring fact. Erasable TypeScript only, so
// `node tests/checks/electronics/rich-bundle.ts <folder>` runs it by hand.
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const SAMPLE = resolve(HERE, '..', '..', 'support', 'sample-bundle')
const SRC = { file: 'sample/notes.md', line: 1 }

export const BLOCKS = [
  { id: 'pg_hub', label: 'Hub chip', refs: ['ZQ1', 'ZQ2'] },
  { id: 'pg_mics', label: 'Sound pickups', refs: ['ZQ3', 'ZQ4', 'ZQ5', 'ZQ6'] },
  { id: 'pg_mem', label: 'Memory', refs: ['ZQ7'] },
  { id: 'pg_view', label: 'Display', refs: ['ZQ8', 'ZQ9'] },
  { id: 'pg_pwr', label: 'Supply', refs: ['ZQ10', 'ZQ11'] },
  { id: 'pg_ctl', label: 'Controls', refs: ['ZQ12'] },
  { id: 'pg_ext', label: 'Outside link', refs: ['ZQ13'] },
]
const PLACED: { name: string; ref: string; side: 'top' | 'bottom'; x: number; y: number; w: number; h: number }[] = [
  { name: 'zq_hub', ref: 'ZQ1', side: 'top', x: -2, y: 1, w: 6, h: 5 },
  { name: 'zq_pick_a', ref: 'ZQ3', side: 'bottom', x: -11, y: 5, w: 4, h: 3 },
  { name: 'zq_pick_b', ref: 'ZQ4', side: 'bottom', x: 9, y: 5, w: 4, h: 3 },
  { name: 'zq_mem', ref: 'ZQ7', side: 'top', x: 7, y: -3, w: 5, h: 4 },
  { name: 'zq_coil', ref: 'ZQ10', side: 'top', x: -8, y: -4, w: 4, h: 4 },
  { name: 'zq_lamp', ref: 'ZQ12', side: 'bottom', x: 3, y: -6, w: 1, h: 1 },
  { name: 'zq_loose', ref: '', side: 'top', x: 0, y: -6, w: 2, h: 1 },
]

const table = (columns: string[], rows: string[][]) => ({ columns, rows, source: SRC })

function pageSvg(title: string, n: number): string {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 280" width="400" height="280"><rect width="400" height="280" fill="#fff"/><rect x="20" y="20" width="360" height="240" fill="none" stroke="#111" stroke-width="2"/><text x="40" y="60" font-size="22" fill="#111">${title}</text><text x="40" y="90" font-size="14" fill="#111">page ${n}</text><rect x="120" y="120" width="160" height="90" fill="none" stroke="#111"/><text x="150" y="170" font-size="18" fill="#111">ZQ chip</text></svg>`
}

export function makeRichBundle(dest: string, opts: { routed?: boolean; schematic?: boolean } = {}): string {
  rmSync(dest, { recursive: true, force: true })
  cpSync(SAMPLE, dest, { recursive: true })
  const read = (f: string) => JSON.parse(readFileSync(join(dest, f), 'utf8'))
  const write = (f: string, v: unknown) => {
    mkdirSync(dirname(join(dest, f)), { recursive: true })
    writeFileSync(join(dest, f), typeof v === 'string' ? v : JSON.stringify(v, null, 2))
  }

  write('electronics.json', {
    blocks: BLOCKS.map((b) => ({ id: b.id, label: b.label, sheet: b.id, part_ids: b.refs.map((r) => `ring:${r}`) })),
    links: [
      { from: 'pg_hub', to: 'pg_mics', nets: ['NET_A', 'NET_B', 'NET_C'] },
      { from: 'pg_hub', to: 'pg_mem', nets: ['NET_D'] },
      { from: 'pg_hub', to: 'pg_view', nets: ['NET_E', 'NET_F'] },
      { from: 'pg_hub', to: 'pg_pwr', nets: ['NET_G'] },
      { from: 'pg_hub', to: 'pg_ctl', nets: ['NET_H'] },
      { from: 'pg_pwr', to: 'pg_view', nets: ['NET_I'] },
      { from: 'pg_pwr', to: 'pg_ext', nets: ['NET_J'] },
    ],
    pin_plan: table(['Signal', 'Pin', 'Ball', 'Notes'], Array.from({ length: 14 }, (_, i) => [`SIG_${i + 1}`, `P${i + 1}`, `B${i + 1}`, i % 5 === 0 ? 'spare test pad' : ''])),
    power_budget: table(['Item', 'Current', 'Notes'], [['From the cell', '12 mA', 'made up'], ['Hub chip', '3 mA', ''], ['Display', '5 mA', '']]),
  })

  const withSvg = opts.schematic !== false
  const pages = [{ id: 'pg_top', title: 'Overview', refs: [] as string[] }, ...BLOCKS.map((b) => ({ id: b.id, title: b.label, refs: b.refs }))]
  write('schematic/index.json', {
    exporter: { tool: 'made-up-exporter', version: null },
    pages: pages.map((p, i) => ({
      id: p.id, title: p.title, number: i + 1, svg: withSvg ? `schematic/${p.id}.svg` : null, pdf: 'sample/zz.pdf',
      part_ids: p.refs.map((r) => `ring:${r}`), source: { file: `sample/${p.id}.kicad_sch`, line: 1 },
    })),
  })
  if (withSvg) pages.forEach((p, i) => write(`schematic/${p.id}.svg`, pageSvg(p.title, i + 1)))

  const base = read('parts.json')
  const proto = base.lines[0]
  const refs = BLOCKS.flatMap((b) => b.refs)
  const lines = refs.map((r, i) => ({
    ...proto, item: `Made-up part ${r}`, refs: [r], part_ids: [`ring:${r}`], row: 10 + i, quantity: 1, maker_part_number: `ZQ-${r}`, source: { file: 'sample/bom.csv', line: 10 + i },
  }))
  base.lines = [...base.lines.filter((l: { bom: string }) => l.bom === 'case'), ...lines]
  base.totals.ring = { lines: lines.length, parts: lines.length, priced_lines: lines.length, unpriced_lines: 0 }
  base.totals.case = { lines: 1, parts: 1, priced_lines: 0, unpriced_lines: 1 }
  write('parts.json', base)

  const notes = read('content/part-notes.json')
  notes.notes = Object.fromEntries(PLACED.filter((p) => p.ref).map((p) => [`ring:${p.ref}`, { checked_against: 'sample section', model_names: [p.name], what: `Made-up part ${p.ref}`, why: 'Only a test sample.' }]))
  write('content/part-notes.json', notes)

  const placements = read('placements.json')
  placements.layers = [{ ...placements.layers[0], id: 'zq_board', label: 'Zq board' }]
  const proto2 = placements.placements[0]
  placements.placements = PLACED.map((p) => ({ ...proto2, name: p.name, layer: 'zq_board' }))
  write('placements.json', placements)

  write('board/index.json', {
    routed: opts.routed === true,
    outline: { x: 0, y: 0, w: 27, h: 17, source: SRC },
    svg: { top: null, bottom: null },
    placements: PLACED.map((p) => ({ name: p.name, part_id: p.ref ? `ring:${p.ref}` : null, x: p.x, y: p.y, w: p.w, h: p.h, side: p.side })),
    missing: opts.routed === true ? [] : ['made-up.kicad_pcb'],
    notches: [{ name: 'zq_notch', x: 13, y: 0, w: 3, h: 6, edge: 'right', position_known: true, source: SRC }],
  })
  return dest
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const out = process.argv[2]
  if (!out) throw new Error('usage: node rich-bundle.ts <folder>')
  makeRichBundle(resolve(out))
  console.log(`rich bundle written to ${resolve(out)}`)
}

// Made-up sample data for the card's own tests and its headless harness. Test-only folder.
import type { Files, PartNotes, Parts, PartsLine } from '../../../contract'

const src = { file: 'sample/bom.csv', line: 2 }

export const legend: Parts['evidence_legend'] = [
  { code: 'DS', meaning: 'read from the maker datasheet', source: src },
  { code: 'LIST', meaning: 'from a distributor listing', source: src },
  { code: 'CALC', meaning: 'calculated, not measured', source: src },
]

export const files: Files = {
  files: [
    { path: 'sample/bom.csv', size_bytes: 10, modified: '2026-01-01T00:00:00Z', area: 'parts', tracked: true },
    { path: 'sample/cell.pdf', size_bytes: 10, modified: '2026-01-01T00:00:00Z', area: 'parts', tracked: true },
  ],
  bundle: null,
}

const base: Omit<PartsLine, 'item' | 'refs' | 'part_ids'> = {
  bom: 'ring', row: 2, quantity: 1, function: null, maker: null, maker_part_number: null, package: null, size_mm: null,
  value: null, key_figures: null, evidence: null, sources: [], price: null, open_action: null, source: src,
}

/** a part waiting on a supplier: no order code, an open action */
export const waiting: PartsLine = {
  ...base, item: 'Made-up cell', refs: ['BT1'], part_ids: ['ring:BT1'], size_mm: '4.6 x 13.0 x 25.0',
  key_figures: '135 mAh minimum', maker: 'Zzmaker', open_action: 'quote from Grepow', evidence: 'LIST', price: null,
  sources: [
    { raw: 'sample/cell.pdf', path: 'sample/cell.pdf', url: null, on_disk: true },
    { raw: 'sample/missing-quote.pdf', path: 'sample/missing-quote.pdf', url: null, on_disk: false },
  ],
}

/** a part with an order code */
export const ordered: PartsLine = {
  ...base, item: 'Made-up chip', refs: ['ZZ9'], part_ids: ['ring:ZZ9'], size_mm: '1 x 2 x 3', maker: 'Zzmaker',
  maker_part_number: 'ZQ-4412-X', package: 'made-up pkg', value: '10 kOhm', evidence: 'DS',
  price: { amount: 1, currency: 'GBP', raw: 'GBP 1.00' },
  sources: [{ raw: 'sample/cell.pdf', path: 'sample/cell.pdf', url: null, on_disk: true }],
}

export const notes: PartNotes['notes'] = {
  'ring:BT1': { what: 'Battery cell', why: 'Stores the energy for the whole ring.', checked_against: 'sample', model_names: ['cell'] },
  'ring:ZZ9': { what: 'Made-up chip.', why: 'Only a test sample.', checked_against: 'sample', model_names: [] },
}

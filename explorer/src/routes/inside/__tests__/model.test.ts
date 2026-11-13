// inside-C05 .. C08: the pure helpers, on made-up sample data (no ring value).
import { describe, expect, it } from 'vitest'
import type { PartPlacements, Parts, PartsLine, RingModel } from '../../../contract'
import { fold, layerRows, objectsOfLayer, partIdsOfObject, searchParts, MAX_RESULTS, type Notes } from '../model'

const src = { file: 'x', line: 1 }
const line = (o: Partial<PartsLine> & { refs: string[] }): PartsLine =>
  ({ bom: 'ring', evidence: null, function: '', item: 'Thing', key_figures: null, maker: null, maker_part_number: null, open_action: null, package: null, part_ids: o.refs.map((r) => `ring:${r}`), price: null, quantity: 1, row: 1, size_mm: null, source: src, sources: [], ...o }) as unknown as PartsLine
const LINES = [
  line({ refs: ['ZA1'], item: 'Alpha widget', maker: 'Würth Elektronik' }),
  line({ refs: ['ZB1', 'ZB2'], item: 'Beta pair', maker_part_number: 'D+X-9' }),
  line({ refs: ['ZC1'], item: 'Gamma (x4)' }),
]
const NOTES: Notes = {
  'ring:ZA1': { what: 'A sample widget.', why: 'Because Ünïcode.', checked_against: '-', model_names: ['obj_a'] },
  'ring:ZC1': { what: 'Gamma note.', why: 'why', checked_against: '-', model_names: ['obj_c'] },
}

describe('inside-C05 search', () => {
  it('is case- and accent-insensitive', () => {
    expect(fold('Würth')).toBe('wurth')
    expect(searchParts(LINES, NOTES, 'WURTH').map((h) => h.id)).toEqual(['ring:ZA1'])
    expect(searchParts(LINES, NOTES, 'wurth')).toEqual(searchParts(LINES, NOTES, 'WÜRTH'))
  })
  it('never treats the text as a pattern', () => {
    expect(() => searchParts(LINES, NOTES, '(')).not.toThrow()
    expect(searchParts(LINES, NOTES, '(').map((h) => h.id)).toEqual(['ring:ZC1'])
    expect(searchParts(LINES, NOTES, 'D+').map((h) => h.id)).toEqual(['ring:ZB1'])
    expect(searchParts(LINES, NOTES, '[')).toEqual([])
    expect(searchParts(LINES, NOTES, '   ')).toEqual([])
  })
  it('selects the matching ref of a grouped line, and searches the note', () => {
    expect(searchParts(LINES, NOTES, 'zb2')[0]?.id).toBe('ring:ZB2')
    expect(searchParts(LINES, NOTES, 'unicode')[0]?.id).toBe('ring:ZA1')
  })
  it('lists at most MAX_RESULTS, exact reference first', () => {
    const many = Array.from({ length: 20 }, (_, i) => line({ refs: [`Q${i}`], item: 'Same item' }))
    const hits = searchParts([...many, line({ refs: ['SAME'], item: 'other' })], null, 'same')
    expect(hits).toHaveLength(MAX_RESULTS)
    expect(hits[0]?.id).toBe('ring:SAME')
  })
  it('lists the case never', () => {
    const c = line({ refs: ['ZA1'], bom: 'case' as never })
    expect(searchParts([c].filter((l) => l.bom === 'ring'), NOTES, 'za1')).toEqual([])
  })
})

const PLACE = {
  layers: [
    { id: 'l1', label: 'First', order: 0, z_min: 0, z_max: 1, source: src },
    { id: 'l2', label: 'Second', order: 1, z_min: 1, z_max: 2, source: src },
  ],
  placements: [
    { name: 'obj_a', layer: 'l1' }, { name: 'obj_c', layer: 'l1' }, { name: 'obj_free', layer: 'l2' },
  ],
} as unknown as PartPlacements
const RING = { nodes: [{ name: 'obj_free', layer: 'l2', kind: 'plain', part_ids: ['ring:ZB1'] }, { name: 'obj_c', layer: 'l1', kind: 'plain', part_ids: [] }] } as unknown as RingModel
const PARTS = { lines: LINES } as unknown as Parts

describe('inside-C06 layers and objects', () => {
  it('one row per layer in record order with its part count', () => {
    expect(layerRows(PLACE)).toEqual([{ id: 'l1', label: 'First', count: 2 }, { id: 'l2', label: 'Second', count: 1 }])
    expect(layerRows(null)).toEqual([])
  })
  it('links an object by the notes first, then by the model', () => {
    expect(partIdsOfObject('obj_a', NOTES, RING)).toEqual(['ring:ZA1'])
    expect(partIdsOfObject('obj_c', NOTES, RING)).toEqual(['ring:ZC1'])
    expect(partIdsOfObject('obj_free', NOTES, RING)).toEqual(['ring:ZB1'])
    expect(partIdsOfObject('nothing_here', NOTES, RING)).toEqual([])
  })
  it('names an object by its parts-list item, or by its own name when no line names it', () => {
    expect(objectsOfLayer('l1', PLACE, PARTS, NOTES, RING).map((o) => o.label)).toEqual(['Alpha widget', 'Gamma (x4)'])
    const lone = { ...PLACE, placements: [{ name: 'lone_object', layer: 'l1' }] } as unknown as PartPlacements
    expect(objectsOfLayer('l1', lone, PARTS, NOTES, RING)).toEqual([{ name: 'lone_object', partId: null, label: 'lone object', ref: null }])
  })
})

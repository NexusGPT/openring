// inside-C19 .. C21: which parts are made to drawing and which maker files belong to a part, on made-up data.
import { describe, expect, it } from 'vitest'
import type { Files, PartsLine } from '../../../contract'
import { fileFor, firstSize, isMadeToDrawing, makerFiles, sheetFor, viewFor, MFG_ROOT } from '../makerFiles'

const line = (o: Partial<PartsLine> & { refs: string[] }): PartsLine =>
  ({ bom: 'ring', maker: null, maker_part_number: null, open_action: null, ...o }) as unknown as PartsLine
const files = (paths: string[]): Files => ({ files: paths.map((path) => ({ path, size_bytes: 1, modified: '', area: 'inside', tracked: true })), bundle: null })
const withFields = (rows: { path: string; part_ids?: string[]; kind?: string; ring_size?: number | null }[]): Files =>
  ({ files: rows.map((r) => ({ size_bytes: 1, modified: '', area: 'inside', tracked: true, ...r })), bundle: null }) as unknown as Files
const P = (n: string) => `${MFG_ROOT}${n}`

describe('inside-C19 made to drawing', () => {
  it('needs no maker, no order code, and an open action that asks for a drawing or an outline', () => {
    expect(isMadeToDrawing(line({ refs: ['ZA'], open_action: 'a maker must answer: drawing per ring size' }))).toBe(true)
    expect(isMadeToDrawing(line({ refs: ['ZA'], open_action: 'The OUTLINE and a quote' }))).toBe(true)
    expect(isMadeToDrawing(line({ refs: ['ZA'], open_action: 'footprint only, nothing to buy' }))).toBe(false)
    expect(isMadeToDrawing(line({ refs: ['ZA'], maker: 'Some Co', open_action: 'a drawing' }))).toBe(false)
    expect(isMadeToDrawing(line({ refs: ['ZA'], maker_part_number: 'X-1', open_action: 'a drawing' }))).toBe(false)
    expect(isMadeToDrawing(line({ refs: ['ZA'] }))).toBe(false)
    expect(isMadeToDrawing(null)).toBe(false)
  })
})

describe('inside-C20 maker files of a part', () => {
  const l = line({ refs: ['ZB1', 'ZB2'] })
  const f = files([
    P('parts/ZB1-size9.stl'), P('parts/ZB1-size11.stl'), P('parts/zb1_size9.step'), P('parts/ZB1-drawing.pdf'), P('parts/ZB1-spec.pdf'),
    P('parts/ZB1-front-size9.svg'), P('parts/ZB1-top.svg'), P('parts/OTHER-front.svg'), P('parts/ZB10-front.svg'),
    'design/other/ZB1-size9.stl', P('parts/ZB1-notes.png'), P('parts/ZB2-side.svg'),
  ])
  const set = makerFiles(f, l)
  it('takes only files under the maker folder whose path carries one of the references as a whole word', () => {
    const paths = set.files.map((x) => x.path)
    expect(paths).not.toContain('design/other/ZB1-size9.stl')
    expect(paths).not.toContain(P('parts/OTHER-front.svg'))
    expect(paths).not.toContain(P('parts/ZB10-front.svg'))
    expect(paths).not.toContain(P('parts/ZB1-notes.png'))
    expect(paths).toContain(P('parts/ZB2-side.svg'))
  })
  it('reads the ring sizes and gives the file of the chosen size, else the one for every size', () => {
    expect(set.sizes).toEqual([9, 11])
    expect(fileFor(set, 'stl', 11)?.path).toBe(P('parts/ZB1-size11.stl'))
    expect(fileFor(set, 'stl', 9)?.path).toBe(P('parts/ZB1-size9.stl'))
    expect(fileFor(set, 'step', 9)?.path).toBe(P('parts/zb1_size9.step'))
    expect(fileFor(set, 'step', 11)).toBeNull() // only size 9 is made: the button for 11 is greyed
    expect(fileFor(set, 'drawing', 9)?.path).toBe(P('parts/ZB1-drawing.pdf'))
    expect(fileFor(set, 'spec', null)?.path).toBe(P('parts/ZB1-spec.pdf'))
  })
  it('says null for a file that is not made yet, never a made-up path', () => {
    expect(fileFor(makerFiles(f, line({ refs: ['ZQ9'] })), 'stl', null)).toBeNull()
    expect(fileFor(makerFiles(null, l), 'stl', null)).toBeNull()
    expect(makerFiles(f, null).files).toEqual([])
  })
})

describe('inside-C21 flat views', () => {
  const set = makerFiles(files([P('ZB1/front-size9.svg'), P('ZB1/front-size11.svg'), P('ZB1/top.svg')]), line({ refs: ['ZB1'] }))
  it('finds a view by its word, per ring size, and reports a missing one as null', () => {
    expect(viewFor(set, 'front', 11)?.path).toBe(P('ZB1/front-size11.svg'))
    expect(viewFor(set, 'top', 11)?.path).toBe(P('ZB1/top.svg'))
    expect(viewFor(set, 'side', 9)).toBeNull()
  })
})

describe('inside-C34 files that say which part they are for', () => {
  const l = line({ refs: ['ZB1'], part_ids: ['ring:ZB1'] })
  const f = withFields([
    { path: P('parts/widget/widget.stl'), part_ids: ['ring:ZB1'], kind: 'stl', ring_size: null },
    { path: P('parts/widget/widget-us9.step'), part_ids: ['ring:ZB1'], kind: 'step', ring_size: 9 },
    { path: P('parts/widget/widget-us11.step'), part_ids: ['ring:ZB1'], kind: 'step', ring_size: 11 },
    { path: P('drawings/widget.svg'), part_ids: ['ring:ZB1'], kind: 'view', ring_size: null },
    { path: P('drawings/widget-us11.svg'), part_ids: ['ring:ZB1'], kind: 'view', ring_size: 11 },
    { path: P('drawings/widget.pdf'), part_ids: ['ring:ZB1'], kind: 'drawing', ring_size: null },
    { path: P('specs/widget.md'), part_ids: ['ring:ZB1'], kind: 'specification', ring_size: null },
    { path: P('parts/other/other.stl'), part_ids: ['ring:ZQ2'], kind: 'stl', ring_size: null },
    { path: P('parts/ZB1-lookalike.stl') },
  ])
  const set = makerFiles(f, l)
  it('belongs to the part named in part_ids, whatever the path says; the path rule is not used for such a file', () => {
    expect(set.files.map((x) => x.path)).not.toContain(P('parts/other/other.stl'))
    expect(fileFor(set, 'stl', null)?.path).toBe(P('parts/widget/widget.stl'))
    expect(fileFor(set, 'spec', null)?.path).toBe(P('specs/widget.md'))
  })
  it('takes kind and ring size from the fields; the default size is 9 when the part has it, else the smallest', () => {
    expect(set.sizes).toEqual([9, 11])
    expect(firstSize(set)).toBe(9)
    expect(firstSize({ files: [], sizes: [11, 13] })).toBe(11)
    expect(fileFor(set, 'step', 11)?.path).toBe(P('parts/widget/widget-us11.step'))
  })
  it('a view svg with no view word is one sheet, per size with a fall back to the unsized one', () => {
    expect(sheetFor(set, 11)?.path).toBe(P('drawings/widget-us11.svg'))
    expect(sheetFor(set, 9)?.path).toBe(P('drawings/widget.svg'))
    expect(viewFor(set, 'front', 9)).toBeNull()
  })
})

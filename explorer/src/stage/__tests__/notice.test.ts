import { describe, expect, it } from 'vitest'
import { noticeFor, pickParams } from '../SceneStage'

describe('stage notice when there is nothing to draw', () => {
  it('stays quiet while loading and while a view exists', () => {
    expect(noticeFor(true, undefined, undefined, 0)).toBeNull()
    expect(noticeFor(false, 'ok', undefined, 1)).toBeNull()
  })
  it('missing record -> missing; unreadable -> unparsed with the file', () => {
    expect(noticeFor(false, 'missing', undefined, 0)).toEqual({ kind: 'missing' })
    expect(noticeFor(false, undefined, undefined, 0)).toEqual({ kind: 'missing' })
    expect(noticeFor(false, 'unparsed', 'ring-model.json', 0)).toEqual({ kind: 'unparsed', file: 'ring-model.json' })
  })
})

describe('pick writes the address', () => {
  const nodes = [{ name: 'with_line', part_ids: ['ring:A1'] }, { name: 'no_line', part_ids: [] }]
  it('a node with a parts-list line sets ?part, one without sets ?object, empty space clears both', () => {
    expect(pickParams(new URLSearchParams(), nodes, { node: 'with_line' }).toString()).toBe('part=ring%3AA1')
    expect(pickParams(new URLSearchParams('part=ring:A1'), nodes, { node: 'no_line' }).toString()).toBe('object=no_line')
    expect(pickParams(new URLSearchParams('object=no_line&x=1'), nodes, null).toString()).toBe('x=1')
  })
})

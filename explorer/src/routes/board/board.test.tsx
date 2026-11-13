// The Board screen's helpers and parts, on made-up data (no ring value): the picker groups, the plan of one board, the copper layer
// choice, the state line in the data's own words, the link back to the connections. Check ids: wiring-screens-C20..C32.
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { Router } from '../../app/router'
import type { ConnectionMap } from '../../components/wiring/wiringModel'
import { BoardPicker } from './BoardPicker'
import { ConnectionsOfBoard } from './ConnectionsOfBoard'
import { LayerToggle } from './LayerToggle'
import { StateLine } from './StateLine'
import { groupsOf, layerChoice, layersShown, pickEntry, planOf, stampWords, type BoardEntry } from './model'

afterEach(cleanup)

const outline = { x: 5, y: 3, w: 10, h: 6, source: { file: 'zz/b.kicad_pcb', line: 4 } }
const entry = (id: string, group: string, over: Partial<BoardEntry> = {}): BoardEntry => ({
  id, group, title: `ZZ board ${group}`, what: `ZZ what ${group}`, size_label: null, file: 'zz/b.kicad_pcb', file_time: '2026-11-13 06:41', outline,
  layers: [
    { id: 'F.ZZ', label: 'Top zz', svg: `board/${id}/F.svg`, items: 3 },
    { id: 'In1.ZZ', label: 'Inner zz 1', svg: `board/${id}/I.svg`, items: 0 },
    { id: 'B.ZZ', label: 'Bottom zz', svg: null, items: 2 },
  ],
  placements: [{ ref: 'ZR1', part_id: 'ring:ZR1', value: '1k', x: 4, y: 2, w: 1, h: 0.5, side: 'top' }, { ref: 'ZR2', part_id: null, value: null, x: 6, y: 4, w: 1, h: 1, side: 'bottom' }],
  missing: [], notes: [], state: { status: 'not-finished', words: 'not finished: 3 connections open, 2 violations', violations: 2, open_connections: 3, checked_at: '2026-11-13 06:43', report: `board/${id}/drc.rpt`, report_lines: [], source: null },
  ...over,
})
const BOARDS = [entry('zz-ring', 'zz-g'), entry('zz-band-us7', 'zz-b', { size_label: 'US 7' }), entry('zz-band-us9', 'zz-b', { size_label: 'US 9' })]

describe('board helpers', () => {
  test('wiring-screens-C20 groups keep the order of the list; a band group holds its sizes', () => {
    const g = groupsOf(BOARDS)
    expect(g.map((x) => [x.id, x.entries.length])).toEqual([['zz-g', 1], ['zz-b', 2]])
    expect(groupsOf(null)).toEqual([])
  })
  test('wiring-screens-C21 the entry of a size; an unknown size falls back to the first', () => {
    const g = groupsOf(BOARDS)[1]!
    expect(pickEntry(g, 'US 9').id).toBe('zz-band-us9')
    expect(pickEntry(g, 'US 99').id).toBe('zz-band-us7')
    expect(pickEntry(g, null).id).toBe('zz-band-us7')
  })
  test('wiring-screens-C22 the plan of an entry names its parts by reference and keeps their face', () => {
    const p = planOf(BOARDS[0]!)
    expect(p.placements.map((x) => [x.name, x.side, x.part_id])).toEqual([['ZR1', 'top', 'ring:ZR1'], ['ZR2', 'bottom', null]])
    expect(p.routed).toBe(false)
    expect(planOf(entry('zz-ok', 'zz-g', { state: { ...BOARDS[0]!.state, status: 'routed-checked' } })).routed).toBe(true)
  })
  test('wiring-screens-C23 the layer choice: a layer by id, all, none; a wrong id falls back to the first layer', () => {
    const e = BOARDS[0]!
    expect(layerChoice(e, null)).toBe('F.ZZ')
    expect(layerChoice(e, 'B.ZZ')).toBe('B.ZZ')
    expect(layerChoice(e, 'all')).toBe('all')
    expect(layerChoice(e, 'none')).toBe('none')
    expect(layerChoice(e, 'nope')).toBe('F.ZZ')
    expect(layerChoice(null, 'all')).toBe('none')
    expect(layerChoice(entry('zz-nolayer', 'zz-g', { layers: [] }), null)).toBe('none')
  })
  test('wiring-screens-C24 stacked layers draw the bottom first; a layer without a picture is left out', () => {
    const e = BOARDS[0]!
    expect(layersShown(e, 'all').map((l) => l.id)).toEqual(['In1.ZZ', 'F.ZZ'])
    expect(layersShown(e, 'F.ZZ').map((l) => l.id)).toEqual(['F.ZZ'])
    expect(layersShown(e, 'B.ZZ')).toEqual([])
    expect(layersShown(e, 'none')).toEqual([])
  })
  test('wiring-screens-C25 a date and time in words', () => {
    expect(stampWords('2026-11-13 06:41')).toBe('13 Nov 2026, 06:41')
    expect(stampWords('2026-11-13T06:43:00')).toBe('13 Nov 2026, 06:43')
    expect(stampWords(null)).toBeNull()
    expect(stampWords('not a date')).toBe('not a date')
  })
})

describe('board parts', () => {
  test('wiring-screens-C26 the picker has one button per board and the size row only for a group with sizes', () => {
    const groups = groupsOf(BOARDS)
    const onGroup = vi.fn()
    const onSize = vi.fn()
    const a = render(<BoardPicker groups={groups} group={groups[0]!} size={null} onGroup={onGroup} onSize={onSize} />)
    expect(screen.getAllByTestId('board.pick-board')).toHaveLength(2)
    expect(screen.queryAllByTestId('board.pick-size')).toHaveLength(0)
    fireEvent.click(screen.getAllByTestId('board.pick-board')[1] as HTMLElement)
    expect(onGroup).toHaveBeenCalledWith('zz-b')
    a.unmount()
    render(<BoardPicker groups={groups} group={groups[1]!} size="US 7" onGroup={onGroup} onSize={onSize} />)
    expect(screen.getAllByTestId('board.pick-size').map((x) => x.getAttribute('data-size'))).toEqual(['US 7', 'US 9'])
    fireEvent.click(screen.getAllByTestId('board.pick-size')[1] as HTMLElement)
    expect(onSize).toHaveBeenCalledWith('US 9')
  })
  test('wiring-screens-C27 the layer buttons carry the data names, all layers and no copper; a layer without a picture is off', () => {
    const onChange = vi.fn()
    render(<LayerToggle entry={BOARDS[0]!} choice="F.ZZ" onChange={onChange} />)
    const btns = screen.getAllByTestId('board.layer')
    expect(btns.map((b) => b.textContent)).toEqual(['Top zz', 'Inner zz 1', 'Bottom zz'])
    expect((btns[2] as HTMLButtonElement).disabled).toBe(true)
    fireEvent.click(screen.getByTestId('board.layer-all'))
    expect(onChange).toHaveBeenCalledWith('all')
    fireEvent.click(screen.getByTestId('board.layer-none'))
    expect(onChange).toHaveBeenCalledWith('none')
  })
  test('wiring-screens-C28 the state line gives the data words, the board file time and the check time', () => {
    render(<StateLine entry={BOARDS[0]!} files={null} />)
    expect(screen.getByTestId('board.state-words').textContent).toBe('not finished: 3 connections open, 2 violations')
    expect(screen.getByTestId('board.state').getAttribute('data-status')).toBe('not-finished')
    expect(screen.getByTestId('board.state').textContent).toContain('13 Nov 2026, 06:41')
    expect(screen.getByTestId('board.state').textContent).toContain('rules check of 13 Nov 2026, 06:43')
  })
  test('wiring-screens-C29 a board with no file or a check that did not run says so and the notes show', () => {
    const e = entry('zz-gone', 'zz-g', {
      file: null, file_time: null, outline: null, layers: [], placements: [], missing: ['zz/gone.kicad_pcb'],
      notes: ['The board file is older than its netlist.'],
      state: { status: 'not-checked', words: 'the board file is not there: zz/gone.kicad_pcb', violations: null, open_connections: null, checked_at: null, report: null, report_lines: [], source: null },
    })
    render(<StateLine entry={e} files={null} />)
    expect(screen.getByTestId('board.state-words').textContent).toContain('not there')
    expect(screen.getByTestId('board.state').textContent).toContain('No board file')
    expect(screen.getByTestId('board.state').textContent).toContain('older than its netlist')
    expect(screen.getByTestId('board.state').textContent).toContain('Missing: zz/gone.kicad_pcb')
  })
  test('wiring-screens-C30 a finished board is not painted as open', () => {
    const e = entry('zz-fin', 'zz-g', { state: { ...BOARDS[0]!.state, status: 'routed-checked', words: 'routed and checked: 0 violations, 0 open connections' } })
    render(<StateLine entry={e} files={null} />)
    expect(screen.getByTestId('board.state').getAttribute('data-status')).toBe('routed-checked')
  })
  test('wiring-screens-C31 the connections of the board link to Electronics; none means no section', () => {
    const map: ConnectionMap = {
      source: { file: 'zz/j.md', line: 1 }, file_time: null, stated_count: 1, note: null,
      nodes: [{ id: 'zz-n', label: 'ZZ node', kind: 'board' as const, board: 'zz-g', scope: null, part_ids: [] }, { id: 'zz-m', label: 'ZZ other', kind: 'part' as const, board: null, scope: null, part_ids: [] }],
      connections: [{
        id: 'ZK1', signal: 'ZZ', ends: [{ node: 'zz-n', text: 'a' }, { node: 'zz-m', text: 'b' }] as [{ node: string; text: string }, { node: string; text: string }], how: { kind: 'zz', text: 'zz', conductors: '1' },
        drawn: { state: 'not-drawn' as const, words: 'NOT DRAWN' }, details: [], proof: [], source: { file: 'zz/j.md', line: 2 },
      }],
    }
    const a = render(<Router memory="/board"><ConnectionsOfBoard map={map} group="zz-g" /></Router>)
    const link = screen.getByTestId('board.connection-link')
    expect(link.getAttribute('href')).toContain('/electronics?conn=ZK1')
    expect(link.textContent).toContain('not drawn')
    a.unmount()
    const b = render(<Router memory="/board"><ConnectionsOfBoard map={map} group="zz-none" /></Router>)
    expect(b.container.querySelector('section')).toBeNull()
    b.unmount()
    const c = render(<Router memory="/board"><ConnectionsOfBoard map={null} group="zz-g" /></Router>)
    expect(c.container.querySelector('section')).toBeNull()
  })
})

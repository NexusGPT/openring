// The connection map of Electronics, on made-up data (no ring value): layout, parallel lines, the map, the list, the detail,
// and the honest states (no map in the data, a count that differs, a joint no file draws). Check ids: wiring-screens-C01..C12.
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { Router } from '../../app/router'
import { ConnectionList } from './ConnectionList'
import { ConnectionMap } from './ConnectionMap'
import { WiringSection } from './WiringSection'
import { connectionsOfBoard, edgesOf, isOpen, layoutNodes, matchesConnection, shiftOf, type Connection, type ConnectionMap as Map_ } from '../../components/wiring/wiringModel'

afterEach(cleanup)

const src = { file: 'zz/joints.md', line: 5 }
const conn = (id: string, a: string, b: string, over: Partial<Connection> = {}): Connection => ({
  id, signal: `ZZ_NET_${id}`, ends: [{ node: a, text: `ZZ end A of ${id}` }, { node: b, text: `ZZ end B of ${id}` }],
  how: { kind: 'zz solder', text: 'zz carrier', conductors: '2' }, drawn: { state: 'drawn', words: `Drawn in ZZ file for ${id}` },
  details: [], proof: [{ file: 'zz/netlist.csv', lines: [3, 9], section: null }], source: src, ...over,
})
const MAP: Map_ = {
  source: src, file_time: '2026-01-02 03:04', stated_count: 4, note: null,
  nodes: [
    { id: 'zz-hub', label: 'ZZ hub board', kind: 'board', board: 'zz-g', scope: null, part_ids: [] },
    { id: 'zz-a', label: 'ZZ circuit A', kind: 'board', board: 'zz-h', scope: null, part_ids: [] },
    { id: 'zz-p', label: 'ZZ part P', kind: 'part', board: null, scope: 'ring', part_ids: ['ring:ZZ1'] },
    { id: 'zz-q', label: 'ZZ part Q', kind: 'part', board: null, scope: 'case', part_ids: [] },
    { id: 'zz-lone', label: 'ZZ lone', kind: 'part', board: null, scope: null, part_ids: [] },
  ],
  connections: [
    conn('Z1', 'zz-hub', 'zz-a'),
    conn('Z2', 'zz-a', 'zz-p'),
    conn('Z3', 'zz-a', 'zz-p', { drawn: { state: 'not-drawn', words: 'NOT DRAWN: zz' } }),
    conn('Z4', 'zz-lone', 'zz-q'),
  ],
}

describe('wiring model', () => {
  test('wiring-screens-C01 parallel connections are numbered so they can be drawn side by side', () => {
    const e = edgesOf(MAP).filter((x) => x.a === 'zz-a' && x.b === 'zz-p')
    expect(e.map((x) => [x.id, x.k, x.m])).toEqual([['Z2', 0, 2], ['Z3', 1, 2]])
    expect(shiftOf(0, 2)).toBeLessThan(0)
    expect(shiftOf(1, 2)).toBeGreaterThan(0)
    expect(shiftOf(0, 1)).toBe(0)
  })
  test('wiring-screens-C02 levels follow the distance from one end of the longest chain; a separate part starts at the top again', () => {
    const l = layoutNodes(MAP)
    const at = (id: string) => l.places.get(id) ?? { x: -1, y: -1 }
    expect(l.places.size).toBe(MAP.nodes.length)
    expect(l.levels).toBe(3)
    expect(l.across).toBe(2)
    // the chain hub, a, p reads top to bottom
    expect(at('zz-hub').y).toBeLessThan(at('zz-a').y)
    expect(at('zz-a').y).toBeLessThan(at('zz-p').y)
    // the pair that is not joined to the rest starts at the top again, beside the first part
    expect(at('zz-lone').y).toBe(at('zz-hub').y)
    expect(at('zz-q').y).toBe(at('zz-a').y)
    expect(at('zz-lone').x).not.toBe(at('zz-hub').x)
    for (const p of l.places.values()) {
      expect(p.x).toBeGreaterThan(0)
      expect(p.x).toBeLessThan(100)
      expect(p.y).toBeGreaterThan(0)
      expect(p.y).toBeLessThan(100)
    }
    // two nodes of one level never share a place
    const keys = new Set([...l.places.values()].map((p) => `${p.x}/${p.y}`))
    expect(keys.size).toBe(MAP.nodes.length)
  })
  test('wiring-screens-C03 an end that names no node is left out of the lines, not drawn to nowhere', () => {
    const bad: Map_ = { ...MAP, connections: [...MAP.connections, conn('Z9', 'zz-hub', 'zz-missing')] }
    expect(edgesOf(bad).some((e) => e.id === 'Z9')).toBe(false)
  })
  test('wiring-screens-C04 the connections of a board group, the open ones, and the typed word', () => {
    expect(connectionsOfBoard(MAP, 'zz-h').map((c) => c.id)).toEqual(['Z1', 'Z2', 'Z3'])
    expect(connectionsOfBoard(MAP, 'zz-nothing')).toEqual([])
    expect(connectionsOfBoard(null, 'zz-h')).toEqual([])
    expect(MAP.connections.filter(isOpen).map((c) => c.id)).toEqual(['Z3'])
    const z2 = MAP.connections[1] as Connection
    expect(matchesConnection(MAP, z2, 'zz_net_z2')).toBe(true)
    expect(matchesConnection(MAP, z2, 'no such word')).toBe(false)
    expect(matchesConnection(MAP, z2, '')).toBe(true)
  })
})

describe('connection map and list', () => {
  test('wiring-screens-C05 one pill per connection; the open one is marked; a click chooses it', () => {
    const pick = vi.fn()
    render(<ConnectionMap map={MAP} selected={null} onSelect={pick} />)
    const pills = screen.getAllByTestId('electronics.conn-pill')
    expect(pills.map((p) => p.getAttribute('data-conn')).sort()).toEqual(['Z1', 'Z2', 'Z3', 'Z4'])
    expect(pills.find((p) => p.getAttribute('data-conn') === 'Z3')?.hasAttribute('data-open')).toBe(true)
    expect(pills.find((p) => p.getAttribute('data-conn') === 'Z1')?.hasAttribute('data-open')).toBe(false)
    fireEvent.click(pills.find((p) => p.getAttribute('data-conn') === 'Z2') as HTMLElement)
    expect(pick).toHaveBeenCalledWith('Z2')
    expect(screen.getAllByTestId('electronics.conn-node')).toHaveLength(MAP.nodes.length)
  })
  test('wiring-screens-C06 the list shows every connection, filters by a typed word and says not drawn', () => {
    const pick = vi.fn()
    render(<ConnectionList map={MAP} selected="Z1" onSelect={pick} />)
    expect(screen.getAllByTestId('electronics.conn-row')).toHaveLength(4)
    const z3 = screen.getAllByTestId('electronics.conn-row').find((r) => r.getAttribute('data-conn') === 'Z3') as HTMLElement
    expect(within(z3).getByText('not drawn')).toBeTruthy()
    fireEvent.change(screen.getByTestId('electronics.conn-find'), { target: { value: 'zz end a of z4' } })
    expect(screen.getAllByTestId('electronics.conn-row')).toHaveLength(1)
    fireEvent.click(screen.getByTestId('electronics.conn-row-button'))
    expect(pick).toHaveBeenCalledWith('Z4')
    fireEvent.change(screen.getByTestId('electronics.conn-find'), { target: { value: 'nothing like this' } })
    expect(screen.getByText('No connection matches.')).toBeTruthy()
  })
})

function section(over: Partial<React.ComponentProps<typeof WiringSection>> = {}) {
  const props: React.ComponentProps<typeof WiringSection> = {
    map: MAP, view: 'map', selected: null, part: null, parts: null, notes: null, files: null, areaState: null,
    boardGroups: ['zz-g'], loading: false, onView: vi.fn(), onSelect: vi.fn(), onPart: vi.fn(), ...over,
  }
  return render(<Router memory="/electronics"><WiringSection {...props} /></Router>)
}

describe('the section', () => {
  test('wiring-screens-C07 data without the map says so in words', () => {
    section({ map: null })
    expect(screen.getByTestId('electronics.conn-none').textContent).toContain('not in the data yet')
    expect(screen.queryByTestId('electronics.conn-map')).toBeNull()
  })
  test('wiring-screens-C08 while the data loads it shows no false absence', () => {
    section({ map: null, loading: true })
    expect(screen.queryByTestId('electronics.conn-none')).toBeNull()
  })
  test('wiring-screens-C09 the count line names the joints no file draws and a differing count is said', () => {
    section({ map: { ...MAP, note: 'the file states 5 joints; its table holds 4' } })
    expect(screen.getByTestId('electronics.conn-count').textContent).toContain('4 connections')
    expect(screen.getByTestId('electronics.conn-count').textContent).toContain('1 not drawn in a design file')
    expect(screen.getByTestId('electronics.conn-note').textContent).toContain('5 joints')
  })
  test('wiring-screens-C10 a chosen connection shows its two ends, signal, carrier, state and proof', () => {
    section({ selected: 'Z3' })
    const d = screen.getByTestId('electronics.conn-detail')
    expect(d.textContent).toContain('ZZ circuit A to ZZ part P')
    expect(screen.getByTestId('electronics.conn-state').textContent).toContain('Not drawn in any design file')
    expect(screen.getAllByTestId('electronics.conn-end')).toHaveLength(2)
    expect(d.textContent).toContain('ZZ_NET_Z3')
    expect(d.textContent).toContain('zz solder')
    expect(within(screen.getByTestId('electronics.conn-proof')).getByText(/zz\/netlist\.csv/)).toBeTruthy()
    expect(d.textContent).toContain('lines 3, 9')
  })
  test('design-sync-C20 a joint stated in text only is open, in its own words, with its conductor count in one line of the detail panel', () => {
    const text = conn('Z5', 'zz-lone', 'zz-q', { drawn: { state: 'text-only', words: 'Stated in text only: zz' }, conductors: { complete: 3, total: 5 } })
    section({ map: { ...MAP, connections: [...MAP.connections, text] }, selected: 'Z5' })
    expect(screen.getByTestId('electronics.conn-state').textContent).toContain('Stated in text only: no design file draws it.')
    expect(screen.getByTestId('electronics.conn-conductors').textContent).toContain('3 of 5 conductors complete')
    cleanup()
    section({ selected: 'Z2' })
    expect(screen.queryByTestId('electronics.conn-conductors')).toBeNull()
  })
  test('wiring-screens-C11 an end that is a board known to the board list links to it; an unknown board does not', () => {
    section({ selected: 'Z1' })
    const links = screen.getAllByTestId('electronics.conn-open-board')
    expect(links).toHaveLength(1)
    expect(links[0]?.getAttribute('href')).toContain('/board?board=zz-g')
  })
  test('wiring-screens-C12 a part end offers its part references; a click asks for the card', () => {
    const onPart = vi.fn()
    section({ selected: 'Z2', onPart })
    fireEvent.click(screen.getByTestId('electronics.conn-part'))
    expect(onPart).toHaveBeenCalledWith('ring:ZZ1')
  })
  test('wiring-screens-C13 the map and the list switch by the view prop; an empty list says so', () => {
    const a = section({ view: 'list' })
    expect(screen.getByTestId('electronics.conn-list')).toBeTruthy()
    a.unmount()
    section({ map: { ...MAP, connections: [], nodes: [] } })
    expect(screen.getByText('The list holds no connection.')).toBeTruthy()
  })
})

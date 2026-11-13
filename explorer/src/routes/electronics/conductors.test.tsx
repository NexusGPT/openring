// The conductors of a connection on made-up data (no ring value): the rows shown equal the record, the count line of the whole
// product, the row that opens, and the honest states (file missing or unreadable, a connection with no conductor line, a count that
// differs). Check ids: conductor-view-C01..C12.
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { Router } from '../../app/router'
import { WiringSection } from './WiringSection'
import type { Connection, ConnectionMap as Map_ } from '../../components/wiring/wiringModel'

afterEach(cleanup)

const src = { file: 'zz/joints.md', line: 5 }
type Cond = NonNullable<Connection['conductor_lines']>[number]
const cond = (id: string, line: number, over: Partial<Cond> = {}): Cond => ({
  id, signal_a: `ZZ_SIG_${id}_A`, signal_b: `ZZ_SIG_${id}_B`,
  first: { board: `ZZ board ${id}`, part: `ZZP${id}`, pin: `${line} (zz pin)`, face: 'zz face top', join: `zz join first ${id}` },
  last: { board: `ZZ other ${id}`, part: `ZZQ${id}`, pin: `${line + 1}`, face: 'zz face bottom', join: `zz join last ${id}` },
  carrier: { kind: 'zz-copper', text: `zz carrier text ${id}` }, state: 'zz-state-ok', state_reason: `zz reason ${id}`,
  lengths: [{ size: 'ZZ 1', kind: 'copper', mm: `${line}.5` }, { size: 'ZZ 2', kind: 'copper', mm: `${line}.75` }],
  source: { file: 'zz/wiring.csv', line }, ...over,
})
const conn = (id: string, over: Partial<Connection> = {}): Connection => ({
  id, signal: `ZZ_NET_${id}`, ends: [{ node: 'zz-a', text: `ZZ end A of ${id}` }, { node: 'zz-b', text: `ZZ end B of ${id}` }],
  how: { kind: 'zz solder', text: 'zz carrier', conductors: '2' }, drawn: { state: 'drawn', words: `Drawn in ZZ file for ${id}` },
  details: [], proof: [], source: src, ...over,
})
const LINES = [cond('ZW1', 2), cond('ZW2', 3, { state: 'zz-state-open' }), cond('ZW3', 4, { lengths: [] })]
const NONE = { id: 'ZW9', reason: 'ZZ NO CONDUCTOR, a gap', state: 'zz-text-only', state_reason: 'zz why', source: { file: 'zz/wiring.csv', line: 9 } }
const MAP: Map_ = {
  source: src, file_time: null, stated_count: 3, note: null,
  nodes: [
    { id: 'zz-a', label: 'ZZ A', kind: 'board', board: null, scope: null, part_ids: [] },
    { id: 'zz-b', label: 'ZZ B', kind: 'part', board: null, scope: 'ring', part_ids: [] },
  ],
  connections: [
    conn('Z1', { conductors: { complete: 2, total: 3 }, conductor_lines: LINES }),
    conn('Z2'),
    conn('Z3', { conductors: { complete: 0, total: 1 }, conductor_lines: [cond('ZW4', 7), cond('ZW5', 8)] }),
    conn('Z4', { no_conductor: [NONE] }),
  ],
  conductor_file: { source: { file: 'zz/wiring.csv', line: null }, status: 'ok', note: null, complete: 9, total: 11, no_conductor: 1 },
}

function section(over: Partial<React.ComponentProps<typeof WiringSection>> = {}) {
  const props: React.ComponentProps<typeof WiringSection> = {
    map: MAP, view: 'map', selected: 'Z1', part: null, parts: null, notes: null, files: null, areaState: null,
    boardGroups: [], loading: false, onView: vi.fn(), onSelect: vi.fn(), onPart: vi.fn(), ...over,
  }
  return render(<Router memory="/electronics"><WiringSection {...props} /></Router>)
}
const size = (s: string) => screen.getAllByTestId('electronics.conductor-size').find((b) => b.dataset.size === s) as HTMLElement
const rows = () => screen.getAllByTestId('electronics.conductor-row')

describe('conductors of a connection', () => {
  test('conductor-view-C01 one row per conductor of the record, with signal, first terminal, last terminal, carrier and state', () => {
    section()
    expect(rows()).toHaveLength(LINES.length)
    LINES.forEach((k, i) => {
      const t = rows()[i]?.textContent ?? ''
      for (const v of [k.id, k.signal_a, k.first.part, k.first.pin, k.last.part, k.last.pin, k.carrier.kind, k.state]) expect(t).toContain(v)
    })
  })
  test('conductor-view-C02 a row shows the second signal when it differs from the first, and one signal when they are equal', () => {
    section({ map: { ...MAP, connections: [conn('Z1', { conductor_lines: [cond('ZW1', 2, { signal_b: 'ZZ_SIG_ZW1_A' })] })] } })
    expect((rows()[0]?.textContent ?? '').match(/ZZ_SIG_ZW1_A/g)).toHaveLength(1)
    cleanup()
    section()
    expect(rows()[0]?.textContent).toContain('ZZ_SIG_ZW1_B')
  })
  test('conductor-view-C03 a row opens to show the join at each end, the source line, and the length for the chosen ring size', () => {
    section()
    expect(screen.queryByTestId('electronics.conductor-open')).toBeNull()
    fireEvent.click(within(rows()[0] as HTMLElement).getByRole('button'))
    const o = screen.getByTestId('electronics.conductor-open').textContent ?? ''
    for (const v of ['zz join first ZW1', 'zz join last ZW1', 'zz face top', 'zz face bottom', 'zz/wiring.csv', 'line 2', 'zz reason ZW1']) expect(o).toContain(v)
    expect(o).toContain('2.5 mm')
    expect(o).not.toContain('2.75 mm')
    fireEvent.click(size('ZZ 2'))
    expect(screen.getByTestId('electronics.conductor-open').textContent).toContain('2.75 mm')
    fireEvent.click(within(rows()[0] as HTMLElement).getByRole('button'))
    expect(screen.queryByTestId('electronics.conductor-open')).toBeNull()
  })
  test('conductor-view-C04 a conductor with no length in the file says so for the chosen size', () => {
    section()
    fireEvent.click(within(rows()[2] as HTMLElement).getByRole('button'))
    expect(screen.getByTestId('electronics.conductor-open').textContent).toContain('no length in the file')
    expect(screen.getAllByTestId('electronics.conductor-size').map((b) => b.dataset.size)).toEqual(['ZZ 1', 'ZZ 2'])
  })
  test('conductor-view-C05 the count line above the map says complete out of total for the whole product, read from the record', () => {
    section()
    expect(screen.getByTestId('electronics.conductor-total').textContent).toContain('9 of 11 conductors complete')
    cleanup()
    section({ map: { ...MAP, conductor_file: { ...(MAP.conductor_file as NonNullable<Map_['conductor_file']>), complete: 4, total: 4 } } })
    expect(screen.getByTestId('electronics.conductor-total').textContent).toContain('4 of 4 conductors complete')
  })
  test('conductor-view-C06 a file that is missing or unreadable is said in words, with no count and no rows shown as fine', () => {
    const f = MAP.conductor_file as NonNullable<Map_['conductor_file']>
    section({ map: { ...MAP, connections: [conn('Z1', { conductors: { complete: 2, total: 3 } })], conductor_file: { ...f, status: 'missing', note: 'zz file is not there', complete: 0, total: 0, no_conductor: 0 } } })
    expect(screen.getByTestId('electronics.conductor-total').textContent).toContain('zz file is not there')
    expect(screen.getByTestId('electronics.conductor-total').textContent).not.toContain('conductors complete')
    expect(screen.getByTestId('electronics.conductor-state').textContent).toContain('zz file is not there')
    expect(screen.queryAllByTestId('electronics.conductor-row')).toHaveLength(0)
    cleanup()
    section({ map: { ...MAP, conductor_file: { ...f, status: 'unreadable', note: 'zz cannot be read', complete: 0, total: 0, no_conductor: 0 } } })
    expect(screen.getByTestId('electronics.conductor-state').textContent).toContain('zz cannot be read')
  })
  test('conductor-view-C07 data without conductor_file (an older bundle) says the list is not in the data, and the screen still works', () => {
    const { conductor_file: _drop, ...older } = MAP
    section({ map: older })
    expect(screen.getByTestId('electronics.conductor-total').textContent).toContain('not in the data')
    expect(screen.getByTestId('electronics.conn-detail')).toBeTruthy()
  })
  test('conductor-view-C08 a connection with no conductor line says so', () => {
    section({ selected: 'Z2' })
    expect(screen.getByTestId('electronics.conductor-state').textContent).toContain('No conductor line of the file names this connection')
    expect(screen.queryAllByTestId('electronics.conductor-row')).toHaveLength(0)
  })
  test('conductor-view-C09 a count that differs from the list is said: the connection says 1, the list shows 2', () => {
    section({ selected: 'Z3' })
    expect(rows()).toHaveLength(2)
    expect(screen.getByTestId('electronics.conductor-state').textContent).toContain('shows 2')
    expect(screen.getByTestId('electronics.conductor-state').textContent).toContain('says 1')
  })
  test('conductor-view-C10 a count that equals the list says nothing about a difference', () => {
    section()
    expect(screen.queryByTestId('electronics.conductor-state')).toBeNull()
  })
  test('conductor-view-C11 a line without a conductor is shown apart, with its reason, and is not a row', () => {
    section({ selected: 'Z4' })
    expect(screen.queryAllByTestId('electronics.conductor-row')).toHaveLength(0)
    const n = screen.getByTestId('electronics.conductor-none').textContent ?? ''
    expect(n).toContain('ZW9')
    expect(n).toContain('ZZ NO CONDUCTOR, a gap')
    expect(n).toContain('line 9')
  })
  test('conductor-view-C12 the rows follow the connection chosen: another connection shows its own conductors', () => {
    const a = section({ selected: 'Z3' })
    expect(rows().map((r) => r.textContent).join()).toContain('ZW4')
    a.unmount()
    section({ selected: 'Z1' })
    expect(rows().map((r) => r.textContent).join()).not.toContain('ZW4')
  })
  test('conductor-view-C13 a count larger than the list is said too: the connection says 5, the list shows 1', () => {
    section({ selected: 'Z5', map: { ...MAP, connections: [...MAP.connections, conn('Z5', { conductors: { complete: 5, total: 5 }, conductor_lines: [cond('ZW6', 11)] })] } })
    expect(screen.getByTestId('electronics.conductor-state').textContent).toContain('shows 1')
    expect(screen.getByTestId('electronics.conductor-state').textContent).toContain('says 5')
  })
})

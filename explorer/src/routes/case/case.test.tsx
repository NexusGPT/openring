// The Case screen's counts line, board parts and the click from a solid to its part card. Made-up data (zz names) for the helpers
// and the board list; the last block reads the bundle built by `npm run collect` through a stubbed fetch in jsdom (skipped when
// it is not built). No browser: jsdom does not draw. Check ids: case-true-C01..C20.
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { QueryClient } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { Router } from '../../app/router'
import { StageSceneProvider } from '../../app/stage-scene'
import type { Case, Parts } from '../../contract'
import { DataProvider } from '../../data'
import { pickParams } from '../../stage/SceneStage'
import { BoardParts } from './BoardParts'
import CaseScreen from './index'
import { Honest } from './Honest'
import { boardOfNode, boardsOfLine, caseLineOf, classWords, countsLine, nodeNames, nodeOf } from './model'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

const board = { key: 'zzmain', title: 'ZZ main board', node: 'zz_board', picker: 'zz-picker', file: 'zz/b.kicad_pcb',
  parts: [{ ref: 'ZU1', value: 'ZZCHIP', part_id: 'case:ZU1', what: 'zz main chip' }, { ref: 'ZWP1', value: 'zz wire end', part_id: null, what: null }] }
const caseRec = {
  glb: { file: 'zz.glb', lid_node: 'zz_lid', hinge: null, nodes: [{ name: 'zz_board', part_ids: ['case:ZB1', 'case:ZU1'] }, { name: 'zz_cap', part_ids: ['case:ZM1'] }, { name: 'zz_bare', part_ids: [] }] },
  facts: [], part_ids: [], supplier_items: [],
  lines: [
    { id: 'case:ZB1', part_ids: ['case:ZB1'], class: 'solid', nodes: ['zz_board'], boards: [], reason: null, source: { file: 'zz/bom.csv', line: 2 } },
    { id: 'case:ZU1', part_ids: ['case:ZU1'], class: 'board', nodes: [], boards: ['zzmain'], reason: null, source: { file: 'zz/bom.csv', line: 3 } },
    { id: 'case:ZH1', part_ids: ['case:ZH1'], class: 'not-fitted', nodes: [], boards: [], reason: 'quantity 0 in the parts list: history only, not fitted', source: { file: 'zz/bom.csv', line: 4 } },
    { id: 'case:ZS1', part_ids: ['case:ZS1'], class: 'no-solid', nodes: [], boards: [], reason: 'zz reason in words', source: { file: 'zz/bom.csv', line: 5 } },
  ],
  counts: { lines: 10, solid: 5, board: 3, not_fitted: 1, no_solid: 1, nodes: 3, nodes_linked: 2, nodes_unlinked: 1 },
  unlinked_nodes: [{ name: 'zz_bare', text: 'no parts-list line' }],
  boards: [board], model: { file: 'zz/params.json', time: '2026-01-02 03:04' }, refit: { item: 'zz', text: 'Zz decided. Zz not done.', source: { file: 'zz/decisions.md', line: 7 } },
} as unknown as Case

describe('case helpers', () => {
  test('case-true-C01 the counts line holds the four numbers of the data and says how many lines', () => {
    expect(countsLine(caseRec)).toBe('10 parts-list lines: 5 in the 3D model, 3 on the boards, 1 not fitted, 1 without a solid')
    expect(countsLine({ ...caseRec, counts: undefined })).toBeNull()
    expect(countsLine(null)).toBeNull()
  })
  test('case-true-C02 a line, its solid and its board are found by part id; a solid with no line is not a board', () => {
    expect(caseLineOf(caseRec, 'case:ZU1')?.class).toBe('board')
    expect(nodeOf(caseRec, 'case:ZU1')?.name).toBe('zz_board')
    expect(boardOfNode(caseRec, 'zz_board')?.key).toBe('zzmain')
    expect(boardOfNode(caseRec, 'zz_cap')).toBeNull()
    expect(boardsOfLine(caseRec, caseLineOf(caseRec, 'case:ZU1')).map((b) => b.key)).toEqual(['zzmain'])
  })
  test('case-true-C03 the words of each class come from the data', () => {
    const w = (id: string) => classWords(caseRec, caseLineOf(caseRec, id)!)
    expect([w('case:ZB1'), w('case:ZU1'), w('case:ZH1'), w('case:ZS1')]).toEqual(['3D', 'zz main board', 'not fitted', 'no solid'])
  })
  test('case-true-C04 a solid is named after its own (first) line, not after a part it carries', () => {
    const parts = { lines: [{ part_ids: ['case:ZU1'], function: 'zz main chip', item: '2' }, { part_ids: ['case:ZB1'], function: 'zz board', item: '1' }] } as unknown as Parts
    expect(nodeNames(caseRec, parts).zz_board).toBe('zz board')
    expect(nodeNames(caseRec, parts).zz_bare).toBe('zz bare')
  })
})

describe('board parts and the honest state', () => {
  test('case-true-C05 a board lists every part with its reference, value and what it is; a part with a line opens its card', () => {
    const picked: string[] = []
    render(<Router memory="/case"><BoardParts board={board} selected={null} onSelect={(id) => picked.push(id)} /></Router>)
    const rows = screen.getAllByTestId('case.board-part')
    expect(rows.map((r) => r.getAttribute('data-ref'))).toEqual(['ZU1', 'ZWP1'])
    expect(rows[0]!.textContent).toContain('zz main chip')
    expect(rows[0]!.textContent).toContain('ZZCHIP')
    fireEvent.click(rows[0]!.querySelector('button')!)
    expect(picked).toEqual(['case:ZU1'])
    expect(rows[1]!.querySelector('button')).toBeNull() // no parts-list line: nothing to open, said as plain text
  })
  test('case-true-C06 "open this board" goes to the Board screen on the board of the data', () => {
    render(<Router memory="/case"><BoardParts board={board} selected={null} onSelect={() => undefined} /></Router>)
    expect(screen.getByTestId('case.open-board').getAttribute('href')).toContain('/board?board=zz-picker')
  })
  test('case-true-C07 the model line and the refit sentence come from the data; nothing without them', () => {
    const { container } = render(<Honest model={caseRec.model} refit={caseRec.refit} />)
    expect(screen.getByTestId('case.model-source').textContent).toContain('zz/params.json, file time 2026-01-02 03:04')
    expect(screen.getByTestId('case.refit').textContent).toContain('Zz decided. Zz not done.')
    expect(screen.getByTestId('case.refit').textContent).toContain('zz/decisions.md, line 7')
    cleanup()
    const none = render(<Honest model={null} refit={null} />)
    expect(none.container.textContent).toBe('')
    expect(container).toBeTruthy()
  })
})

// ---------------------------------------------------------------- the real bundle

const BUNDLE = join(__dirname, '..', '..', '..', 'public', 'data')
const built = existsSync(join(BUNDLE, 'case', 'index.json')) && existsSync(join(BUNDLE, 'parts.json'))
const read = <T,>(rel: string): T => JSON.parse(readFileSync(join(BUNDLE, rel), 'utf8')) as T

function serve() {
  vi.stubGlobal('matchMedia', () => ({ matches: false, addEventListener: () => undefined, removeEventListener: () => undefined }))
  Element.prototype.scrollIntoView = () => undefined
  vi.stubGlobal('fetch', async (url: string) => {
    const file = join(BUNDLE, String(url).replace(/^\/data\//, ''))
    return existsSync(file) ? new Response(readFileSync(file), { status: 200 }) : new Response('no', { status: 404 })
  })
}

function caseAt(path: string) {
  const client = new QueryClient({ defaultOptions: { queries: { staleTime: Infinity, gcTime: Infinity, retry: false } } })
  return render(
    <DataProvider client={client}>
      <Router memory={path}>
        <StageSceneProvider route="case"><CaseScreen /></StageSceneProvider>
      </Router>
    </DataProvider>,
  )
}

describe.skipIf(!built)('the real bundle', () => {
  test('case-true-C10 a click on any of the solids opens a part card: its first part id is a line of the parts record', () => {
    const c = read<Case>('case/index.json')
    const parts = read<Parts>('parts.json')
    const nodes = c.glb!.nodes
    expect(nodes).toHaveLength(40)
    for (const n of nodes) {
      const next = pickParams(new URLSearchParams(), nodes, { node: n.name })
      const id = next.get('part')
      expect(id, `${n.name} opens a card`).toBeTruthy()
      expect(parts.lines.some((l) => l.part_ids.includes(id!)), n.name).toBe(true)
    }
  })

  test('case-true-C11 the screen shows the counts line of the data and a class on every row of the list', async () => {
    serve()
    const c = read<Case>('case/index.json')
    caseAt('/case')
    await waitFor(() => expect(screen.getByTestId('case.counts-line').textContent).toBe(countsLine(c)))
    const rows = screen.getAllByTestId('case.part-row')
    expect(rows).toHaveLength(c.counts!.lines)
    expect(rows.every((r) => r.getAttribute('data-class'))).toBe(true)
    expect(rows.filter((r) => r.getAttribute('data-class') === 'not fitted')).toHaveLength(c.counts!.not_fitted)
    expect(screen.getByTestId('case.model-source').textContent).toContain(c.model!.time)
  })

  test('case-true-C12 a click on the main board solid offers its parts; a part of it opens the existing part card', async () => {
    serve()
    const c = read<Case>('case/index.json')
    const main = c.boards!.find((b) => b.key === 'main')!
    const first = c.glb!.nodes.find((n) => n.name === main.node)!.part_ids[0]!
    caseAt(`/case?part=${encodeURIComponent(first)}`)
    await waitFor(() => expect(screen.getByTestId('case.board-parts')).toBeTruthy())
    expect(screen.getAllByTestId('case.board-part')).toHaveLength(main.parts.length)
    expect(screen.getByTestId('case.open-board').getAttribute('href')).toContain(`board=${main.picker}`)
    const row = screen.getAllByTestId('case.board-part').find((r) => r.getAttribute('data-ref') === 'U1')!
    fireEvent.click(row.querySelector('button')!)
    await waitFor(() => expect(screen.getByTestId('case.selected-line').textContent).toContain('U1'))
  })

  test('case-true-C13 a click on a solid with a parts-list line (a glide) shows its line and its class "3D"', async () => {
    serve()
    const c = read<Case>('case/index.json')
    const node = c.glb!.nodes.find((n) => n.name.startsWith('glide'))!
    caseAt(`/case?part=${encodeURIComponent(node.part_ids[0]!)}`)
    await waitFor(() => expect(screen.getByTestId('case.selected-class').textContent).toBe('3D'))
    expect(screen.getByTestId('case.selected-line')).toBeTruthy()
  })
})

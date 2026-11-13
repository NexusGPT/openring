// The two screens on the data bundle built by `npm run collect` (public/data), read from disk and served to the screens through a
// stubbed fetch in jsdom. No browser. Skipped when the bundle is not built. It proves the screens read the real new fields without
// a schema or runtime error and show the picker, the state words, the layers and the connections; it does not prove how they look.
// Check ids: wiring-screens-C40..C45.
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { QueryClient } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { Router } from '../../app/router'
import { StageSceneProvider } from '../../app/stage-scene'
import { DataProvider } from '../../data'
import { schemaProblems } from '../../data/validate'
import Board from './index'
import Electronics from '../electronics/index'

const BUNDLE = join(__dirname, '..', '..', '..', 'public', 'data')
const built = existsSync(join(BUNDLE, 'manifest.json')) && existsSync(join(BUNDLE, 'board', 'index.json'))
const read = (rel: string): unknown => JSON.parse(readFileSync(join(BUNDLE, rel), 'utf8'))

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function serve() {
  // jsdom has no matchMedia and no scrollIntoView; the screens ask for both when a choice opens below the fold
  vi.stubGlobal('matchMedia', () => ({ matches: false, addEventListener: () => undefined, removeEventListener: () => undefined }))
  Element.prototype.scrollIntoView = () => undefined
  vi.stubGlobal('fetch', async (url: string) => {
    const rel = String(url).replace(/^\/data\//, '')
    const file = join(BUNDLE, rel)
    if (!existsSync(file)) return new Response('no', { status: 404 })
    return new Response(readFileSync(file), { status: 200 })
  })
}

function screenAt(path: string, ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { staleTime: Infinity, gcTime: Infinity, retry: false } } })
  return render(
    <DataProvider client={client}>
      <Router memory={path}>
        <StageSceneProvider route={path.startsWith('/board') ? 'board' : 'electronics'}>{ui}</StageSceneProvider>
      </Router>
    </DataProvider>,
  )
}

describe.skipIf(!built)('the real bundle', () => {
  test('wiring-screens-C40 the new fields pass the browser schemas', () => {
    expect(schemaProblems('board-files', read('board/index.json'))).toEqual([])
    expect(schemaProblems('electronics', read('electronics.json'))).toEqual([])
  })

  test('wiring-screens-C41 Board: a picker with every board of the data, the state words of the shown board, its layers', async () => {
    serve()
    const data = read('board/index.json') as { boards: { group: string; state: { words: string }; layers: { label: string }[] }[] }
    screenAt('/board', <Board />)
    await waitFor(() => expect(screen.getAllByTestId('board.pick-board').length).toBeGreaterThan(0))
    expect(screen.getAllByTestId('board.pick-board')).toHaveLength(new Set(data.boards.map((b) => b.group)).size)
    const first = data.boards[0]!
    await waitFor(() => expect(screen.getByTestId('board.state-words').textContent).toBe(first.state.words))
    expect(screen.getAllByTestId('board.layer').map((b) => b.textContent)).toEqual(first.layers.map((l) => l.label))
    expect(screen.getAllByTestId('board.plan-mark').length).toBeGreaterThan(0)
    expect(screen.getAllByTestId('board.plan-picture')).toHaveLength(1)
  })

  test('wiring-screens-C42 Board: all layers stack one picture per layer; a band circuit offers its ring sizes', async () => {
    serve()
    const data = read('board/index.json') as { boards: { group: string; size_label: string | null; layers: unknown[] }[] }
    const ring = data.boards.find((b) => b.group === 'ring')!
    screenAt('/board?layer=all', <Board />)
    await waitFor(() => expect(screen.getAllByTestId('board.plan-picture').length).toBe(ring.layers.length))
    cleanup()
    const band = data.boards.find((b) => b.size_label)!
    screenAt(`/board?board=${band.group}`, <Board />)
    await waitFor(() => expect(screen.getAllByTestId('board.pick-size').length).toBe(data.boards.filter((b) => b.group === band.group).length))
  })

  test('wiring-screens-C43 Board: a click on a part opens its card or the words for an object without a parts-list line', async () => {
    serve()
    screenAt('/board', <Board />)
    await waitFor(() => expect(screen.getAllByTestId('board.plan-mark').length).toBeGreaterThan(0))
    fireEvent.click(screen.getAllByTestId('board.plan-mark')[0] as HTMLElement)
    await waitFor(() => expect(screen.getByTestId('board.card-slot')).toBeTruthy())
  })

  test('wiring-screens-C44 Electronics: the connection map has one pill per connection; a click shows the two ends', async () => {
    serve()
    const map = (read('electronics.json') as { connection_map: { connections: { id: string }[]; stated_count: number } }).connection_map
    screenAt('/electronics', <Electronics />)
    await waitFor(() => expect(screen.getAllByTestId('electronics.conn-pill').length).toBe(map.connections.length))
    expect(map.connections.length).toBe(map.stated_count)
    fireEvent.click(screen.getAllByTestId('electronics.conn-pill')[0] as HTMLElement)
    await waitFor(() => expect(screen.getAllByTestId('electronics.conn-end')).toHaveLength(2))
  })

  test('wiring-screens-C45 Electronics: a deep link opens a connection; its board end links to the Board screen', async () => {
    serve()
    const map = (read('electronics.json') as { connection_map: { connections: { id: string; ends: { node: string }[] }[]; nodes: { id: string; kind: string }[] } }).connection_map
    const withBoard = map.connections.find((c) => c.ends.some((e) => map.nodes.find((n) => n.id === e.node)?.kind === 'board'))!
    screenAt(`/electronics?conn=${withBoard.id}&cview=list`, <Electronics />)
    await waitFor(() => expect(screen.getByTestId('electronics.conn-detail').getAttribute('data-conn')).toBe(withBoard.id))
    expect(screen.getByTestId('electronics.conn-list')).toBeTruthy()
    await waitFor(() => expect(screen.getAllByTestId('electronics.conn-open-board').length).toBeGreaterThan(0))
  })
})

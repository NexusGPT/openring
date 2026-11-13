// The Electronics screen on the data bundle built by `npm run collect` (public/data), served through a stubbed fetch in jsdom.
// No browser. Skipped when the bundle is not built. For every connection of the real record: the rows shown equal its conductor
// lines, and the count line above the map equals the conductor_file record. Check ids: conductor-view-C20..C22.
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { QueryClient } from '@tanstack/react-query'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, test, vi } from 'vitest'
import { Router } from '../../app/router'
import { StageSceneProvider } from '../../app/stage-scene'
import { DataProvider } from '../../data'
import { schemaProblems } from '../../data/validate'
import Electronics from './index'
import type { Electronics as Rec } from '../../contract'

const BUNDLE = join(__dirname, '..', '..', '..', 'public', 'data')
const built = existsSync(join(BUNDLE, 'electronics.json'))
const record = (): NonNullable<Rec['connection_map']> => (JSON.parse(readFileSync(join(BUNDLE, 'electronics.json'), 'utf8')) as Rec).connection_map as NonNullable<Rec['connection_map']>

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function open(conn: string) {
  vi.stubGlobal('matchMedia', () => ({ matches: false, addEventListener: () => undefined, removeEventListener: () => undefined }))
  Element.prototype.scrollIntoView = () => undefined
  vi.stubGlobal('fetch', async (url: string) => {
    const file = join(BUNDLE, String(url).replace(/^\/data\//, ''))
    return existsSync(file) ? new Response(readFileSync(file), { status: 200 }) : new Response('no', { status: 404 })
  })
  const client = new QueryClient({ defaultOptions: { queries: { staleTime: Infinity, gcTime: Infinity, retry: false } } })
  return render(
    <DataProvider client={client}>
      <Router memory={`/electronics?conn=${conn}`}>
        <StageSceneProvider route="electronics"><Electronics /></StageSceneProvider>
      </Router>
    </DataProvider>,
  )
}

describe.skipIf(!built)('the real bundle', () => {
  test('conductor-view-C20 the electronics record with the conductor fields passes the browser schema', () => {
    expect(schemaProblems('electronics', JSON.parse(readFileSync(join(BUNDLE, 'electronics.json'), 'utf8')))).toEqual([])
  })
  test('conductor-view-C21 for each connection with conductor lines the rows shown equal the record, in order', async () => {
    for (const c of record().connections.filter((x) => (x.conductor_lines ?? []).length > 0)) {
      const view = open(c.id)
      await waitFor(() => expect(screen.getAllByTestId('electronics.conductor-row').length).toBeGreaterThan(0))
      expect(screen.getAllByTestId('electronics.conductor-row').map((r) => r.getAttribute('data-conductor'))).toEqual((c.conductor_lines ?? []).map((k) => k.id))
      view.unmount()
    }
  }, 120_000)
  test('conductor-view-C22 the count line above the map equals the complete and total conductors of the record', async () => {
    const f = record().conductor_file
    open('R1')
    await waitFor(() => expect(screen.getByTestId('electronics.conductor-total')).toBeTruthy())
    expect(f?.status).toBe('ok')
    expect(screen.getByTestId('electronics.conductor-total').textContent).toContain(`${f?.complete} of ${f?.total} conductors complete`)
  })
})

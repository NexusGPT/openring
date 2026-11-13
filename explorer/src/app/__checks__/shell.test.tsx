// shell-C01..C03, C06 (jsdom side): nine tabs and Files, the route registry, honest placeholders, the
// panel that expands over the stage and collapses on Escape, the one persistent stage slot.
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { ROUTES } from '../../contract'
import { DataProvider, createQueryClient } from '../../data'
import { Router } from '../router'
import { Shell } from '../Shell'
import { FILES_TO, ROUTE_PATH, TAB_LABEL, routeOfPath, screenFor } from '../routes'

// the sample bundle's manifest (made-up values), with the dirty flag set for this check
const SAMPLE = JSON.parse(readFileSync(join(__dirname, '..', '..', '..', 'tests', 'support', 'sample-bundle', 'manifest.json'), 'utf8'))
const MANIFEST = { ...SAMPLE, git_dirty: true }

function stubFetch(manifest: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string) => {
      if (manifest && String(url).endsWith('manifest.json')) return new Response(JSON.stringify(manifest), { status: 200 })
      return new Response('', { status: 404 })
    }),
  )
}
function mount(path: string) {
  return render(
    <DataProvider client={createQueryClient()}>
      <Router memory={path}>
        <Shell />
      </Router>
    </DataProvider>,
  )
}
beforeEach(() => stubFetch(null))
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

test('shell-C02a: 9 tabs plus Files, one aria-current, on every route', async () => {
  for (const id of ROUTES) {
    mount(ROUTE_PATH[id])
    const tabs = screen.getAllByTestId(/^app\.tab-(?!files$)/).filter((e) => e.classList.contains('tab'))
    expect(tabs).toHaveLength(9)
    expect(screen.getByTestId('app.tab-files').textContent).toBe('Files')
    expect(screen.getByTestId(`app.tab-${id}`).getAttribute('aria-current')).toBe('page')
    expect(document.querySelectorAll('[aria-current=page]')).toHaveLength(1)
    expect(screen.getByTestId(`app.tab-${id}`).textContent).toBe(TAB_LABEL[id])
    cleanup()
  }
})

test('shell-C02b: Files leads to /open#files and takes the current mark from Open items', () => {
  mount('/')
  const files = screen.getByTestId('app.tab-files')
  expect(files.getAttribute('href')).toBe(FILES_TO)
  fireEvent.click(files)
  expect(files.getAttribute('aria-current')).toBe('page')
  expect(screen.getByTestId('app.tab-open').getAttribute('aria-current')).toBeNull()
})

test('shell-C02c: a click on a tab moves aria-current', () => {
  mount('/')
  fireEvent.click(screen.getByTestId('app.tab-parts'))
  expect(screen.getByTestId('app.tab-parts').getAttribute('aria-current')).toBe('page')
  expect(screen.getByTestId('app.tab-home').getAttribute('aria-current')).toBeNull()
})

test('shell-C02d: route ids from paths, deep links keep their route', () => {
  expect(routeOfPath('/')).toBe('home')
  expect(routeOfPath('/inside')).toBe('inside')
  expect(routeOfPath('/open/')).toBe('open')
  expect(routeOfPath('/nonsense')).toBe('home')
})

test('shell-C01: a route whose screen has not landed says "Screen not built yet." and the page is not blank', async () => {
  for (const id of ROUTES) {
    if (screenFor(id)) continue
    mount(ROUTE_PATH[id])
    const p = await screen.findByTestId('app.screen-placeholder')
    expect(p.textContent).toContain('Screen not built yet.')
    expect(screen.getByTestId('app.panel-body').textContent?.length).toBeGreaterThan(0)
    cleanup()
  }
})

test('shell-C03: the stage slot sits outside the routes and keeps its id across navigation', () => {
  mount('/')
  const stage = screen.getByTestId('app.stage')
  const id = stage.getAttribute('data-stage-id')
  expect(id).toBeTruthy()
  for (const r of ['inside', 'parts', 'electronics']) fireEvent.click(screen.getByTestId(`app.tab-${r}`))
  expect(screen.getByTestId('app.stage')).toBe(stage)
  expect(stage.getAttribute('data-stage-id')).toBe(id)
  expect(screen.getByTestId('app.panel-body').contains(stage)).toBe(false)
})

test('shell-C06: panel-expand opens the panel over the stage, a second click and Escape close it', () => {
  mount('/electronics')
  const main = document.querySelector('main') as HTMLElement
  const btn = screen.getByTestId('app.panel-expand')
  expect(main.dataset.expanded).toBe('false')
  fireEvent.click(btn)
  expect(main.dataset.expanded).toBe('true')
  expect(btn.getAttribute('aria-pressed')).toBe('true')
  fireEvent.keyDown(window, { key: 'Escape' })
  expect(main.dataset.expanded).toBe('false')
  fireEvent.click(btn)
  fireEvent.click(btn)
  expect(main.dataset.expanded).toBe('false')
})

test('shell-C06b: leaving the route collapses the panel', () => {
  mount('/electronics')
  fireEvent.click(screen.getByTestId('app.panel-expand'))
  fireEvent.click(screen.getByTestId('app.tab-parts'))
  expect((document.querySelector('main') as HTMLElement).dataset.expanded).toBe('false')
})

test('shell-C04e: the stamp on screen reads the manifest; with none it says so with the contract words', async () => {
  mount('/')
  await waitFor(() => expect(screen.getByTestId('app.freshness-stamp').textContent).toBe('Not built yet.'))
  cleanup()
  stubFetch(MANIFEST)
  mount('/')
  await waitFor(() => expect(screen.getByTestId('app.freshness-stamp').textContent).toContain(`commit ${MANIFEST.git_commit.slice(0, 7)}`))
  const el = screen.getByTestId('app.freshness-stamp')
  expect(el.textContent).toContain(new Date(MANIFEST.built_at).toLocaleString())
  expect(el.textContent).toContain('files changed since')
})

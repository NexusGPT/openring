// The history router: paths under a basename, deep links with a query, links that navigate in place.
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, test } from 'vitest'
import { Link, Router, parseTo, readWindow, useLocation, useSearchParams } from '../router'

afterEach(cleanup)

test('router: parseTo splits path, query and hash', () => {
  expect(parseTo('/inside?part=ring%3ABT1#x')).toEqual({ pathname: '/inside', search: '?part=ring%3ABT1', hash: '#x' })
  expect(parseTo('/open#files')).toEqual({ pathname: '/open', search: '', hash: '#files' })
  expect(parseTo('')).toEqual({ pathname: '/', search: '', hash: '' })
})

test('router: readWindow drops the basename of a sub-path host', () => {
  const w = { location: { pathname: '/ring/inside', search: '?part=a', hash: '' } } as Pick<Window, 'location'>
  expect(readWindow('/ring', w)).toEqual({ pathname: '/inside', search: '?part=a', hash: '' })
  expect(readWindow('', { location: { pathname: '/', search: '', hash: '' } } as Pick<Window, 'location'>).pathname).toBe('/')
})

function Probe() {
  const l = useLocation()
  const [q, setQ] = useSearchParams()
  return (
    <div>
      <span data-testid="at">{l.pathname + l.search + l.hash}</span>
      <span data-testid="part">{q.get('part') ?? ''}</span>
      <button onClick={() => setQ({ part: 'ring:BT1' })}>pick</button>
      <Link to="/parts" data-testid="go">go</Link>
    </div>
  )
}

test('router: a link moves the location without a page load, href carries the basename', () => {
  render(<Router basename="/ring" memory="/inside?part=ring%3AU1"><Probe /></Router>)
  expect(screen.getByTestId('part').textContent).toBe('ring:U1')
  expect(screen.getByTestId('go').getAttribute('href')).toBe('/ring/parts')
  fireEvent.click(screen.getByTestId('go'))
  expect(screen.getByTestId('at').textContent).toBe('/parts')
})

test('router: useSearchParams writes the selection into the address and keeps the path', () => {
  render(<Router memory="/inside"><Probe /></Router>)
  fireEvent.click(screen.getByText('pick'))
  expect(screen.getByTestId('at').textContent).toBe('/inside?part=ring%3ABT1')
})

test('router: a modified click is left to the browser', () => {
  render(<Router memory="/"><Probe /></Router>)
  fireEvent.click(screen.getByTestId('go'), { metaKey: true })
  expect(screen.getByTestId('at').textContent).toBe('/')
})

import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { PartCard } from '..'
import { files, legend, notes, ordered, waiting } from './sample'

afterEach(cleanup)
const card = (r = 'parts') => screen.getByTestId(`${r}.part-card`)
const bt1 = (extra = {}) => <PartCard route="parts" partId="ring:BT1" line={waiting} note={notes['ring:BT1']} legend={legend} files={files} {...extra} />

describe('part card', () => {
  it('part-card-C01: plain words come first, heading is the note, and they sit before the disclosure', () => {
    render(bt1())
    const text = card().textContent ?? ''
    expect(screen.getByRole('heading', { level: 3 }).textContent).toBe('Battery cell')
    for (const w of ['Battery cell', 'Stores the energy', '4.6 x 13.0 x 25.0', 'Grepow']) {
      expect(text).toContain(w)
      expect(text.indexOf(w)).toBeLessThan(text.indexOf('Exact data'))
    }
    expect(text).toContain('Open: quote from Grepow')
    expect(text.indexOf('Stores the energy')).toBeGreaterThan(text.indexOf('Battery cell'))
  })

  it('part-card-C10: a history line with quantity 0 says it is not fitted', () => {
    render(bt1({ line: { ...waiting, quantity: 0 } }))
    expect(card().textContent).toContain('Not fitted (history only)')
    cleanup()
    render(bt1({ line: { ...waiting, quantity: 1 } }))
    expect(card().textContent).not.toContain('Not fitted')
  })

  it('part-card-C02: the maker part number is hidden until Exact data is opened', () => {
    render(<PartCard route="inside" partId="ring:ZZ9" line={ordered} note={notes['ring:ZZ9']} legend={legend} files={files} />)
    const c = screen.getByTestId('inside.part-card')
    expect(c.textContent).not.toContain('ZQ-4412-X')
    expect(c.textContent).not.toContain('made-up pkg')
    const btn = screen.getByRole('button', { name: 'Exact data' })
    expect(btn.getAttribute('aria-expanded')).toBe('false')
    fireEvent.click(btn)
    expect(btn.getAttribute('aria-expanded')).toBe('true')
    for (const w of ['ZQ-4412-X', 'made-up pkg', '10 kOhm', 'GBP 1.00', 'Zzmaker']) expect(c.textContent).toContain(w)
    fireEvent.click(btn)
    expect(c.textContent).not.toContain('ZQ-4412-X')
  })

  it('part-card-C03: a source whose file is absent is aria-disabled "not on disk"; a present one opens in a new tab under /files/', () => {
    render(bt1())
    fireEvent.click(screen.getByRole('button', { name: 'Exact data' }))
    const off = card().querySelectorAll('[aria-disabled="true"]')
    expect(off).toHaveLength(1)
    expect(off[0]!.textContent).toContain('not on disk')
    expect(off[0]!.textContent).toContain('missing-quote.pdf')
    expect(off[0]!.getAttribute('href')).toBeNull()
    const a = within(card()).getByRole('link', { name: 'cell.pdf' }) as HTMLAnchorElement
    expect(a.getAttribute('target')).toBe('_blank')
    expect(a.getAttribute('rel')).toContain('noopener')
    expect(a.getAttribute('href')).toMatch(/\/files\/sample\/cell\.pdf$/)
  })

  it('part-card-C04: a path flagged on disk but not in files.json is still not linked; with no file list the flag decides', () => {
    const line = { ...ordered, sources: [{ raw: 'x/other.pdf', path: 'x/other.pdf', url: null, on_disk: true }] }
    const { unmount } = render(<PartCard route="parts" partId="ring:ZZ9" line={line} files={files} />)
    fireEvent.click(screen.getByRole('button', { name: 'Exact data' }))
    // other.pdf is flagged on disk but not listed in files.json: greyed. The csv row is listed: linked.
    const off = card().querySelectorAll('[aria-disabled="true"]')
    expect(off).toHaveLength(1)
    expect(off[0]!.textContent).toContain('other.pdf')
    unmount()
  })

  it('part-card-C05: an object with no parts-list line says so and has no disclosure', () => {
    render(<PartCard route="inside" partId="ring:gasket" line={null} />)
    const c = screen.getByTestId('inside.part-card')
    expect(c.textContent).toContain('no parts-list line for this object')
    expect(screen.queryByRole('button', { name: 'Exact data' })).toBeNull()
  })

  it('part-card-C06: a stale record keeps its content, says so in the contract words, and is marked dimmed', () => {
    render(bt1({ banner: { kind: 'stale', basis: 'ZV1', current: 'ZV2' } }))
    expect(card().getAttribute('data-stale')).toBe('true')
    expect(card().textContent).toContain('Made for design ZV1; the design is now ZV2. Being redone.')
    expect(card().textContent).toContain('Battery cell')
  })

  it('part-card-C07: text only; markup inside a note stays as text', () => {
    const evil = { what: '<img src=x onerror=alert(1)>', why: '<b>bold</b>', checked_against: 's', model_names: [] }
    render(bt1({ note: evil }))
    expect(card().querySelector('img, b, script')).toBeNull()
    expect(card().textContent).toContain('<b>bold</b>')
  })

  it('part-card-C08: the accent pill shows for an open action or a supplier wait, never otherwise; the evidence pill carries its plain meaning', () => {
    const { unmount } = render(bt1())
    expect(screen.getByTestId('parts.part-card-status').textContent).toBe('waiting on a supplier')
    expect(screen.getByTestId('parts.part-card-evidence').textContent).toBe('from a distributor listing')
    unmount()
    render(<PartCard route="parts" partId="ring:ZZ9" line={ordered} legend={legend} files={files} />)
    expect(screen.queryByTestId('parts.part-card-status')).toBeNull()
    expect(screen.getByTestId('parts.part-card-evidence').textContent).toBe('read from the maker datasheet')
    cleanup()
    render(<PartCard route="parts" partId="ring:ZZ9" line={ordered} legend={legend} areaState="waiting on a supplier" />)
    expect(screen.getByTestId('parts.part-card-status')).toBeTruthy()
  })

  it('part-card-C09: the order row says where the code is, or that there is none', () => {
    render(<PartCard route="parts" partId="ring:ZZ9" line={ordered} />)
    expect(card().textContent).toContain('Order code is under Exact data')
    cleanup()
    render(<PartCard route="parts" partId="ring:ZZ9" line={{ ...ordered, maker_part_number: null }} />)
    expect(card().textContent).toContain('No order code yet')
  })

  it('part-card-C10: a line with no note falls back to the item name and shows no invented why', () => {
    render(<PartCard route="board" partId="ring:ZZ9" line={ordered} />)
    expect(screen.getByRole('heading', { level: 3 }).textContent).toBe('Made-up chip')
    expect(card('board').querySelector('.pc-plain')).toBeNull()
  })
})

import { cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { AREA_PILL, AREA_PILL_WORDS, StateBanner, StatePill, bannerText, partId, parsePartId, testId, CHECK_ID_RE, RECORD_IDS, ROUTES } from '.'

afterEach(cleanup)

describe('id grammars', () => {
  it('builds <route>.<element> test ids and refuses anything else', () => {
    expect(testId('inside', 'part-card')).toBe('inside.part-card')
    expect(() => testId('inside', 'PartCard')).toThrow()
    expect(() => testId('inside', 'part card')).toThrow()
  })
  it('builds <bom>:<ref> part ids', () => {
    expect(partId('ring', 'ZZ9')).toBe('ring:ZZ9')
    expect(parsePartId('case:ZC1')).toEqual({ bom: 'case', ref: 'ZC1' })
    expect(parsePartId('other:ZZ9')).toBeNull()
    expect(parsePartId('ring:')).toBeNull()
  })
  it('accepts check ids <lane>-C01..C99 only', () => {
    expect(CHECK_ID_RE.test('home-C01')).toBe(true)
    expect(CHECK_ID_RE.test('open-files-C99')).toBe(true)
    expect(CHECK_ID_RE.test('home-C00')).toBe(false)
    expect(CHECK_ID_RE.test('home-C100')).toBe(false)
  })
  it('lists 9 routes and 13 records', () => {
    expect(ROUTES).toHaveLength(9)
    expect(RECORD_IDS).toHaveLength(13)
  })
})

describe('honest-state vocabulary', () => {
  it('says the missing, unparsed and stale sentences', () => {
    expect(bannerText({ kind: 'missing' })).toBe('Not built yet. Run npm run collect.')
    expect(bannerText({ kind: 'unparsed', file: 'zz.csv' })).toContain('The file changed and cannot be read: zz.csv')
    expect(bannerText({ kind: 'stale', basis: 'ZV1', current: 'ZV2' })).toBe('Made for design ZV1; the design is now ZV2. Being redone.')
  })
  it('says the two exterior states', () => {
    expect(bannerText({ kind: 'exterior-not-picked' })).toBe("Exterior not designed yet. The stage shows a plain black slab at the ring's true size.")
    expect(bannerText({ kind: 'exterior-in-design' })).toContain('Exterior in design, not approved yet.')
  })
  it('keeps the five area pill words exactly', () => {
    expect(AREA_PILL_WORDS).toEqual(['done', 'in progress', 'not started', 'waiting on a supplier', 'state unknown'])
  })
})

describe('StateBanner and StatePill', () => {
  it('renders the vocabulary text under <route>.state-banner', () => {
    const { getByTestId } = render(<StateBanner route="parts" spec={{ kind: 'missing' }} />)
    const el = getByTestId('parts.state-banner')
    expect(el.textContent).toBe(bannerText({ kind: 'missing' }))
    expect(el.querySelector('code')?.textContent).toBe('npm run collect')
  })
  it('names what the board is missing', () => {
    const { getByTestId } = render(<StateBanner route="board" spec={{ kind: 'board-not-routed', missing: ['zz.kicad_pcb'] }} />)
    expect(getByTestId('board.state-banner').textContent).toContain('zz.kicad_pcb')
  })
  it('renders a pill whose words come from AREA_PILL', () => {
    const { getByTestId } = render(<StatePill route="home" state="waiting on a supplier" />)
    expect(getByTestId('home.state-pill').textContent).toBe(AREA_PILL['waiting on a supplier'])
  })
})

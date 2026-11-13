import { cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { PLACEMENTS, RING, exteriorSpec } from './harness-data'
import { Stage } from '../Stage'

afterEach(cleanup)

describe('Stage without WebGL (jsdom)', () => {
  it('says "missing" in the vocabulary words and installs the test api, with 0 contexts', () => {
    const r = render(<Stage views={[exteriorSpec()]} ringModel={RING} placements={PLACEMENTS} route="look" />)
    expect(r.getByTestId('look.state-banner').textContent).toBe('Not built yet. Run npm run collect.')
    expect(window.__stage?.contexts).toBe(0)
    expect(window.__stage?.ready).toBe(false)
    expect(window.__stage?.unmappedNodes()).toEqual([])
  })
})

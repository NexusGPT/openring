import { cleanup, render, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { Router } from '../../app/router'
import { DataProvider, createQueryClient } from '../../data'
import SceneStage from '../index'
import { getEngine } from '../engine'

afterEach(cleanup)

describe('SceneStage (the shell mount)', () => {
  it('takes a new scene without remounting and puts the shell slot id on the canvas', () => {
    const client = createQueryClient()
    const wrap = (route: 'home' | 'inside') => (
      <DataProvider client={client}>
        <Router memory="/">
          <div data-stage-id="slot-1">
            <SceneStage scene={{ route, options: { preset: 'top' } }} />
          </div>
        </Router>
      </DataProvider>
    )
    const r = render(wrap('home'))
    const host = r.getByTestId('home.stage')
    expect(getEngine().canvas.dataset.stageId).toBe('slot-1')
    r.rerender(wrap('inside'))
    expect(r.getByTestId('inside.stage')).toBe(host)
  })
  it('with the ring-model record missing the stage says so in the contract words, never blank', async () => {
    const r = render(
      <DataProvider client={createQueryClient()}>
        <Router memory="/">
          <SceneStage scene={{ route: 'inside', options: {} }} />
        </Router>
      </DataProvider>,
    )
    await waitFor(() => expect(r.getByTestId('inside.state-banner').textContent).toBe('Not built yet. Run npm run collect.'))
  })
})

// The light row of the readout is drawn only when the record's light rule says the ring has a recording light. Made-up record.
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import type { FirmwareRules } from '../../../contract'
import type { EngineOutput } from '../engine'
import { Readout } from '../Readout'

afterEach(cleanup)
const rules = (light: boolean) =>
  ({
    states: [{ id: 'ZZ_ON', label: 'Zz on', meaning: 'zz', microphones: 'on' }],
    light_rule: { text: 'zz', on_where_microphones_on: light, source: { file: 'zz', line: 1 } },
  }) as unknown as FirmwareRules
const out = (light: boolean): EngineOutput => ({ state: 'ZZ_ON', light, highlights: 0, recordingMs: null, pulses: [], hold: null, note: null })

describe('behaviour readout light row', () => {
  it('design-sync-C10: a record without a recording light draws no light row and no lamp', () => {
    render(<Readout rules={rules(false)} out={out(false)} />)
    expect(screen.queryByTestId('behaviour.light')).toBeNull()
    expect(screen.queryByText('Light')).toBeNull()
  })
  it('design-sync-C11: a record with a recording light draws the row and it follows the state', () => {
    const a = render(<Readout rules={rules(true)} out={out(true)} />)
    expect(screen.getByTestId('behaviour.light').getAttribute('data-on')).toBe('true')
    a.unmount()
    render(<Readout rules={rules(true)} out={out(false)} />)
    expect(screen.getByTestId('behaviour.light').getAttribute('data-on')).toBe('false')
  })
})

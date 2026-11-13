import type { AreaState } from '../records'
import { AREA_PILL } from '../vocabulary'
import { testId, type TestScope } from '../ids'

/** The state pill of an area. Its words come from AREA_PILL only. Colour is never the only signal. */
export function StatePill({ route, state }: { route: TestScope; state: AreaState }) {
  return (
    <span data-testid={testId(route, 'state-pill')} data-state={state}>
      {AREA_PILL[state]}
    </span>
  )
}

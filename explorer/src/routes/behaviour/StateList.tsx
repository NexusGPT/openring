import type { FirmwareRules } from '../../contract'
import { testId } from '../../contract'

export function StateList({ rules, current }: { rules: FirmwareRules; current: string }) {
  return (
    <ol className="states" data-testid={testId('behaviour', 'state-list')}>
      {rules.states.map((s) => (
        <li key={s.id} className="state-row" data-testid={testId('behaviour', 'state-item')} data-state-id={s.id} title={s.meaning} data-current={s.id === current ? 'true' : 'false'} aria-current={s.id === current ? 'step' : undefined}>
          <span className="state-mark" aria-hidden="true" />
          <span className="state-name">{s.label}</span>
        </li>
      ))}
    </ol>
  )
}

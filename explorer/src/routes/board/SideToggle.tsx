// Top / Bottom / Both: three buttons, the chosen one is aria-pressed.
import { testId } from '../../contract'
import { MODES, type Mode } from './model'

export function SideToggle({ mode, onChange, disabled }: { mode: Mode; onChange: (m: Mode) => void; disabled?: boolean }) {
  return (
    <div className="bd-toggle" role="group" aria-label="Side of the board" data-testid={testId('board', 'sides')}>
      {MODES.map((m) => (
        <button
          key={m.id} type="button" aria-pressed={mode === m.id} disabled={disabled}
          data-testid={testId('board', `side-${m.id}`)} onClick={() => onChange(m.id)}
        >
          {m.label}
        </button>
      ))}
    </div>
  )
}

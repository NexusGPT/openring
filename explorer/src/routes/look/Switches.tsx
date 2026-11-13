// Finish, screen state and view: one segmented group each, applied to every option at once by the stage.
import { useState } from 'react'
import { testId } from '../../contract'
import { LOOK_WORDS, VIEW_CHOICES, type ViewId } from './model'

export interface Choice {
  id: string
  label: string
  colour?: string
  title?: string
}

/** `lead` choices are always shown; the rest (if any) open behind one "More" button, and stay open while one of them is active. */
function Group({ name, label, choices, value, onPick, lead }: { name: string; label: string; choices: Choice[]; value: string | null; onPick: (id: string) => void; lead?: number }) {
  const [open, setOpen] = useState(false)
  const head = lead === undefined ? choices : choices.slice(0, lead)
  const rest = lead === undefined ? [] : choices.slice(lead)
  const expanded = open || rest.some((c) => c.id === value)
  const shown = expanded ? choices : head
  return (
    <div className="sw-row">
      <span className="label sw-name" id={`look-sw-${name}`}>
        {label}
      </span>
      <div className="sw-group" role="group" aria-labelledby={`look-sw-${name}`} data-testid={testId('look', `${name}-switch`)}>
        {shown.map((c) => (
          <button
            key={c.id}
            type="button"
            className="sw-btn"
            aria-pressed={value === c.id}
            title={c.title ?? c.label}
            data-value={c.id}
            data-testid={testId('look', name)}
            onClick={() => onPick(c.id)}
          >
            {c.colour ? <span className="sw-dot" style={{ background: c.colour }} aria-hidden="true" /> : null}
            <span className="sw-text">{c.label}</span>
          </button>
        ))}
        {rest.length ? (
          <button type="button" className="sw-btn sw-more" aria-expanded={expanded} disabled={expanded && rest.some((c) => c.id === value)} data-testid={testId('look', `${name}-more`)} onClick={() => setOpen(!expanded)}>
            {expanded ? LOOK_WORDS.fewer : LOOK_WORDS.more}
          </button>
        ) : null}
      </div>
    </div>
  )
}

export interface SwitchesProps {
  finishes: Choice[]
  finish: string | null
  onFinish(id: string): void
  screens: Choice[]
  screen: string | null
  onScreen(id: string | null): void
  view: ViewId
  onView(id: ViewId): void
}

export function Switches(p: SwitchesProps) {
  // the first two states of the bundle (standby, recording) and Off lead; the others open behind "More"
  const screens = [...p.screens.slice(0, 2), { id: 'off', label: LOOK_WORDS.off }, ...p.screens.slice(2)]
  return (
    <div className="sw" data-testid={testId('look', 'switches')}>
      {p.finishes.length ? (
        <Group name="finish" label={LOOK_WORDS.finish} choices={p.finishes} value={p.finish} onPick={p.onFinish} />
      ) : (
        <p className="sw-none muted">{LOOK_WORDS.noFinishes}</p>
      )}
      <Group name="screen" label={LOOK_WORDS.screen} choices={screens} value={p.screen ?? 'off'} onPick={(id) => p.onScreen(id === 'off' ? null : id)} lead={Math.min(3, screens.length)} />
      <Group name="view" label={LOOK_WORDS.view} choices={[...VIEW_CHOICES]} value={p.view} onPick={(id) => p.onView(id as ViewId)} />
    </div>
  )
}

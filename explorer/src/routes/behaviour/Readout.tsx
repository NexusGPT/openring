// The ring's state at this moment: state name large, light, timer while recording, highlights, vibration.
import type { FirmwareRules } from '../../contract'
import { testId } from '../../contract'
import type { EngineOutput } from './engine'
import { WORDS, clock, stateOf } from './model'

const MARK_PX = 0.35
const MAX_MARKS = 8

export function Readout({ rules, out }: { rules: FirmwareRules; out: EngineOutput }) {
  const s = stateOf(rules, out.state)
  const timer = out.recordingMs !== null
  const marks = out.pulses.slice(-MAX_MARKS)
  // the light is drawn only when the record says the ring has a recording light
  const hasLight = rules.light_rule.on_where_microphones_on
  return (
    <section className="readout" aria-live="polite">
      <p className="label">{WORDS.state}</p>
      <h2 className="display state-name-big" data-testid={testId('behaviour', 'state')} data-state-id={out.state} key={out.state}>
        {s?.label ?? ''}
      </h2>
      <p className="state-meaning-big">{s?.meaning ?? ''}</p>
      <dl className="meters">
        {hasLight && (
          <div className="meter">
            <dt className="label">{WORDS.light}</dt>
            <dd>
              <span className="lamp" data-testid={testId('behaviour', 'light')} data-on={out.light ? 'true' : 'false'} />
              <span className="meter-word">{out.light ? WORDS.lightOn : WORDS.lightOff}</span>
            </dd>
          </div>
        )}
        <div className="meter" data-active={timer ? 'true' : 'false'}>
          <dt className="label">{WORDS.timer}</dt>
          <dd className="timer" data-testid={testId('behaviour', 'timer')}>
            {timer ? clock(out.recordingMs ?? 0) : '—'}
          </dd>
        </div>
        <div className="meter">
          <dt className="label">{WORDS.highlights}</dt>
          <dd data-testid={testId('behaviour', 'highlights')} data-count={out.highlights}>
            <span className="hl-row">
              {Array.from({ length: Math.min(out.highlights, 12) }, (_, i) => (
                <span key={i} className="hl-mark" data-testid={testId('behaviour', 'highlight-mark')} />
              ))}
            </span>
            <span className="meter-word">{out.highlights}</span>
          </dd>
        </div>
      </dl>
      <div className="vib">
        <span className="label">{WORDS.vibration}</span>
        <span className="vib-row" data-testid={testId('behaviour', 'vibration')}>
          {marks.length === 0 ? <span className="vib-none">{WORDS.nothingYet}</span> : null}
          {marks.map((p) => (
            <span key={p.key} className="vib-mark" data-testid={testId('behaviour', 'vibration-mark')} data-on-ms={p.onMs} style={{ width: `${Math.max(3, p.onMs * MARK_PX)}px` }} />
          ))}
        </span>
      </div>
    </section>
  )
}

// The joystick, the ring's one control: four directions around a centre press. A direction is a click; the
// centre is pressed and held (CentrePress). Names and effects come from the firmware-rules record.
import type { FirmwareRules } from '../../contract'
import { testId } from '../../contract'
import { CentrePress } from './CentrePress'
import { WORDS, padArea } from './model'
import type { Behaviour } from './useBehaviour'

export function Joystick({ rules, b, hint, disabled }: { rules: FirmwareRules; b: Behaviour; hint: { text: string; title: string }[]; disabled: boolean }) {
  const centre = rules.joystick.find((j) => padArea(j) === 'c')
  return (
    <div className="joy-wrap">
      <div className="joy" role="group" aria-label={WORDS.joystick} data-testid={testId('behaviour', 'joystick')}>
        {rules.joystick.filter((j) => j !== centre).map((j) => (
          <button
            key={j.direction}
            type="button"
            className="joy-btn"
            data-area={padArea(j)}
            data-direction={j.direction}
            data-testid={testId('behaviour', 'joystick-button')}
            title={j.effect}
            disabled={disabled}
            onClick={() => b.joystick(j.direction)}
          >
            {j.direction}
          </button>
        ))}
        <div className="joy-centre" data-direction={centre?.direction}>
          <CentrePress b={b} title={centre?.effect} disabled={disabled} />
        </div>
      </div>
      <div className="joy-how">
        <p className="joy-lead">{WORDS.centreLead}</p>
        <ul className="rec-hint label">
          {hint.map((t) => (
            <li key={t.text} title={t.title}>{t.text}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

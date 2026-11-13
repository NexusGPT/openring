// Behaviour: how the ring acts. The ring is the shell's stage; this is the panel: the state now, the
// joystick (its centre press is the only button), the light, the timer, highlights, vibration and every state. Every state
// name, time and effect comes from the firmware-rules record, through the engine adapter (engine.ts).
import './behaviour.css'
import { testId } from '../../contract'
import { useRecord } from '../../data'
import { useStageScene } from '../../app/stage-scene'
import { Banner } from './states'
import { Joystick } from './Joystick'
import { Readout } from './Readout'
import { StateList } from './StateList'
import { WORDS, effectsIn, holdHints, screenFor, stateOf } from './model'
import { useRingPress } from './press3d'
import { useBehaviour } from './useBehaviour'

export default function Behaviour() {
  const rulesRec = useRecord('firmware-rules')
  const ringRec = useRecord('ring-model')
  const rs = rulesRec.state
  const rules = rs && (rs.status === 'ok' || rs.status === 'stale') ? rs.data : null
  const ring = ringRec.state?.data ?? null
  const b = useBehaviour(rules)
  const cur = rules ? stateOf(rules, b.out.state) : undefined
  const stale = rs?.status === 'stale'

  const elapsed = b.out.recordingMs === null ? 0 : Math.floor(b.out.recordingMs / 1000)
  useStageScene({ show: 'exterior', preset: 'three-quarter', elapsed, screen: rules && ring ? screenFor(rules, ring, b.out.state) : null, ...(rules?.light_rule.on_where_microphones_on ? { light: b.out.light } : {}) })
  useRingPress(b, !!rules)

  const hint = rules ? holdHints(rules) : []
  const does = rules ? effectsIn(rules, b.out.state) : []
  const loading = rulesRec.loading
  const stamp = rs?.status === 'stale' || rs?.status === 'ok' ? rs.data.design_version : null

  return (
    <div className="behaviour" aria-busy={loading} data-testid={testId('behaviour', 'panel')} data-stage-elapsed={elapsed}>
      <header className="beh-head">
        <h1 className="display">{WORDS.title}</h1>
        {stamp ? <p className="label">Rules for design {stamp}</p> : null}
      </header>
      {!loading ? <Banner id="firmware-rules" state={rs} /> : null}
      {rules ? (
        <div className="beh-body" data-dimmed={stale ? 'true' : undefined}>
          <Readout rules={rules} out={b.out} />
          <section className="controls">
            <h3 className="label">{WORDS.joystick}</h3>
            <Joystick rules={rules} b={b} hint={hint} disabled={false} />
          </section>
          {does.length ? (
            <section className="does">
              <h3 className="label">{WORDS.doesNow}</h3>
              <ul>
                {does.slice(0, 4).map((d) => (
                  <li key={d.kind + d.effect}>
                    <span className="does-kind">{d.kind}</span>
                    <span className="does-effect">{d.effect}</span>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
          <section>
            <h3 className="label">{WORDS.states}</h3>
            <StateList rules={rules} current={b.out.state} />
          </section>
        </div>
      ) : null}
    </div>
  )
}
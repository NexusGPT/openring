// Look: the outside of the ring. The 3D view is the shell's stage; this is the panel on its right:
// the finish, screen state and view switches, and the open exterior options with what each costs.
import './look.css'
import { useMemo, useState } from 'react'
import { StateBanner, testId, type BannerSpec, type RecordId } from '../../contract'
import { RECORD_FILE } from '../../contract'
import { useRecord, type RecordState } from '../../data'
import { useStageScene } from '../../app/stage-scene'
import { OptionPanel } from './OptionPanel'
import { Switches, type Choice } from './Switches'
import { LOOK_WORDS, modeOf, shortLabel, type ViewId } from './model'

function specFor(id: RecordId, s: RecordState<unknown> | null): BannerSpec | null {
  if (!s) return null
  if (s.status === 'missing') return { kind: 'missing' }
  if (s.status === 'unparsed') return { kind: 'unparsed', file: s.entry.source[0] ?? RECORD_FILE[id] }
  if (s.status === 'stale') return { kind: 'stale', basis: s.entry.basis_version ?? '', current: s.entry.current_version ?? '' }
  return null
}
const isDown = (s: RecordState<unknown> | null): boolean => !!s && (s.status === 'missing' || s.status === 'unparsed')

export default function Look() {
  const lookRec = useRecord('look-options')
  const ringRec = useRecord('ring-model')
  const looks = lookRec.state && !isDown(lookRec.state) ? (lookRec.state.data ?? null) : null
  const ring = ringRec.state && !isDown(ringRec.state) ? (ringRec.state.data ?? null) : null
  const loading = lookRec.loading || ringRec.loading
  const mode = modeOf(looks, ring)

  const [finish, setFinish] = useState<string | null>(null)
  const [screen, setScreen] = useState<string | null | undefined>(undefined) // undefined = the bundle's first state
  const [view, setView] = useState<ViewId>('three-quarter')

  const finishes: Choice[] = useMemo(() => (looks?.finishes ?? []).map((f) => ({ id: f.name, label: f.name, colour: f.colour })), [looks])
  const screens: Choice[] = useMemo(() => (ring?.screens.states ?? []).map((s) => ({ id: s.state, label: shortLabel(s.label), title: s.label })), [ring])
  const finishNow = finishes.find((f) => f.id === finish)?.id ?? finishes[0]?.id ?? null
  const screenNow = screen === undefined ? (screens[0]?.id ?? null) : screen

  const picked = !!looks?.picked
  // side by side only when there is something to compare; one option IS the ring's exterior
  const wantLooks = mode.kind === 'options' && !picked && mode.options.filter((o) => o.glb).length > 1
  useStageScene({
    show: wantLooks ? 'looks' : 'exterior',
    preset: view,
    ...(finishNow ? { finish: finishNow } : {}),
    screen: screenNow,
  })

  const status = ring?.exterior.status
  const exteriorBanner: BannerSpec | null =
    mode.kind === 'none' ? null : status === 'in-design' ? { kind: 'exterior-in-design' } : status === 'not-picked' ? { kind: 'exterior-not-picked' } : null
  const everythingDown = isDown(lookRec.state) && isDown(ringRec.state)
  const optionsBanner: BannerSpec | null = mode.kind === 'none' && !loading && !isDown(lookRec.state) ? { kind: 'new-options' } : specFor('look-options', lookRec.state)
  const stale = lookRec.state?.status === 'stale'

  return (
    <div className="look" aria-busy={loading} data-testid={testId('look', 'panel')}>
      <header className="look-head">
        <h1 className="display">{LOOK_WORDS.title}</h1>
      </header>

      {!loading && everythingDown ? (
        <StateBanner route="look" spec={{ kind: 'missing' }} />
      ) : (
        <>
          {exteriorBanner ? <StateBanner route="look" spec={exteriorBanner} /> : null}
          {ring ? (
            <Switches
              finishes={finishes}
              finish={finishNow}
              onFinish={setFinish}
              screens={screens}
              screen={screenNow}
              onScreen={setScreen}
              view={view}
              onView={setView}
            />
          ) : null}
          <section className="sec" aria-labelledby="look-options" data-testid={testId('look', 'options')} data-dimmed={stale ? 'true' : undefined}>
            <h2 className="label sec-title" id="look-options">
              {LOOK_WORDS.options}
            </h2>
            {mode.kind === 'options' ? mode.options.map((o) => <OptionPanel key={o.id} option={o} picked={picked} />) : null}
            {mode.kind === 'fallback' && ring ? (
              <article className="opt" data-testid={testId('look', 'look-option')} data-option={ring.exterior.look_id ?? 'exterior'} data-fallback="true">
                <header className="opt-head">
                  <h3 className="opt-title">{ring.exterior.look_id ?? LOOK_WORDS.fallback}</h3>
                </header>
                <details className="opt-details">
                  <summary>{LOOK_WORDS.details}</summary>
                  <dl>
                    <dt className="label">{LOOK_WORDS.source}</dt>
                    <dd>{ring.exterior.source?.file ?? ring.exterior.file}</dd>
                  </dl>
                </details>
              </article>
            ) : null}
            {optionsBanner ? <StateBanner route="look" spec={optionsBanner} /> : null}
          </section>
        </>
      )}
    </div>
  )
}

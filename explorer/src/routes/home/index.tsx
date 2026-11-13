// Home: the ring at a glance. The ring itself is the shell's stage; this is the panel on its right:
// the key numbers, the state of the 8 areas (each one click from its screen) and what is next for the owner.
import './home.css'
import { StateBanner, testId, type RecordId } from '../../contract'
import { useRecord } from '../../data'
import { useStageScene } from '../../app/stage-scene'
import { TAB_LABEL } from '../../app/route-names'
import { AreaTiles } from './AreaTiles'
import { KeyNumbers } from './KeyNumbers'
import { NextUp } from './NextUp'
import { HOME_WORDS, nextItems } from './model'
import { Banner, isDown } from './states'

function Section({ title, children, id }: { title: string; children: React.ReactNode; id: string }) {
  return (
    <section className="sec" aria-labelledby={`home-${id}`} data-testid={testId('home', `section-${id}`)}>
      <h2 className="label sec-title" id={`home-${id}`}>
        {title}
      </h2>
      {children}
    </section>
  )
}

export default function Home() {
  useStageScene({ show: 'exterior', preset: 'three-quarter' })
  const facts = useRecord('key-numbers')
  const areas = useRecord('area-states')
  const open = useRecord('open-items')
  const ring = useRecord('ring-model')
  const files = useRecord('files')

  const loading = facts.loading || areas.loading || open.loading || ring.loading
  const f = facts.state
  const a = areas.state
  const everythingDown = isDown(f) && isDown(a)
  const next = nextItems(a?.data?.areas ?? null, open.state?.data ?? null, (id) => TAB_LABEL[id])
  const version = f?.data?.design_version ?? a?.data?.design_version ?? null
  const updated = a?.data?.updated ?? null
  const exterior = ring.state?.data?.exterior.status
  const stamp = [version ? `Design ${version}` : null, updated ? `updated ${updated}` : null].filter(Boolean).join(' · ')

  return (
    <div className="home" aria-busy={loading} data-testid={testId('home', 'panel')}>
      <header className="home-head">
        <h1 className="display">{HOME_WORDS.title}</h1>
        {stamp ? <p className="label">{stamp}</p> : null}
      </header>

      {!loading && everythingDown ? (
        <Banner id="key-numbers" state={f} />
      ) : (
        <>
          {exterior === 'in-design' || exterior === 'not-picked' ? <StateBanner route="home" spec={{ kind: exterior === 'in-design' ? 'exterior-in-design' : 'exterior-not-picked' }} /> : null}
          <Section title={HOME_WORDS.keyNumbers} id="numbers">
            {f && (f.status === 'ok' || f.status === 'stale') ? <KeyNumbers rec={f} files={files.state} message={f.entry.message} /> : <Banner id="key-numbers" state={f} />}
            {f?.status === 'stale' ? <Banner id="key-numbers" state={f} /> : null}
          </Section>
          <Section title={HOME_WORDS.areas} id="areas">
            {a && (a.status === 'ok' || a.status === 'stale') ? <AreaTiles rec={a} /> : <Banner id="area-states" state={a} />}
          </Section>
          <Section title={HOME_WORDS.next} id="next">
            {next.length === 0 && isDown(open.state) ? <Banner id="open-items" state={open.state} /> : <NextUp items={next} quiet={!!a} />}
          </Section>
        </>
      )}
    </div>
  )
}

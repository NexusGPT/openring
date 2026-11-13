// Open items and files: what is not finished (who must act), and every project file, ready to hand over.
// The ring is the shell's stage on the left; this is the panel on its right.
import './open.css'
import { useEffect, useRef } from 'react'
import { StatePill, testId } from '../../contract'
import { useRecord } from '../../data'
import { useStageScene } from '../../app/stage-scene'
import { useLocation } from '../../app/router'
import { FILES_HASH } from '../../app/route-names'
import { AreaFiles } from './AreaFiles'
import { BundleCard } from './BundleCard'
import { HandOff } from './HandOff'
import { LeftOut } from './LeftOut'
import { OpenItems } from './OpenItems'
import { OPEN_WORDS } from './model'
import { Banner, hasData } from './states'

/** Bring the files section to the top of the panel on #files, the panel's top otherwise. */
function useHashScroll(target: React.RefObject<HTMLElement | null>, ready: boolean) {
  const { hash } = useLocation()
  useEffect(() => {
    const body = target.current?.closest('.panel-body')
    if (!body || !ready) return
    const top = hash === FILES_HASH ? target.current!.offsetTop - (body as HTMLElement).offsetTop : 0
    body.scrollTo({ top: Math.max(0, top), behavior: 'auto' })
  }, [hash, ready, target])
}

function Section({ id, title, meta, children, innerRef }: { id: string; title: string; meta?: string; children: React.ReactNode; innerRef?: React.Ref<HTMLElement> }) {
  return (
    <section className="sec" id={id} ref={innerRef} aria-labelledby={`open-${id}`} data-testid={testId('open', `section-${id}`)}>
      <h2 className="sec-head" id={`open-${id}`}>
        <span className="label">{title}</span>
        {meta ? <span className="label sec-meta">{meta}</span> : null}
      </h2>
      {children}
    </section>
  )
}

export default function OpenAndFiles() {
  useStageScene({ show: 'exterior', preset: 'three-quarter' })
  const open = useRecord('open-items')
  const files = useRecord('files')
  const areas = useRecord('area-states')
  const filesRef = useRef<HTMLElement | null>(null)
  const loading = open.loading || files.loading
  useHashScroll(filesRef, !loading)

  const o = open.state
  const f = files.state
  const pill = areas.state?.data?.areas.find((a) => a.id === 'open')?.state
  const list = hasData(f) ? (f?.data?.files ?? []) : []

  return (
    <div className="open" aria-busy={loading} data-testid={testId('open', 'panel')}>
      <header className="open-head">
        <h1 className="display">{OPEN_WORDS.title}</h1>
        {pill ? <StatePill route="open" state={pill} /> : null}
      </header>

      <Section id="items" title={OPEN_WORDS.open}>
        <Banner id="open-items" state={o} />
        {o?.data && hasData(o) ? (
          <div data-dimmed={o.status === 'stale' ? 'true' : undefined}>
            <OpenItems data={o.data} files={f} />
          </div>
        ) : null}
      </Section>

      <Section id="files" title={OPEN_WORDS.files} innerRef={filesRef}>
        <Banner id="files" state={f} />
        {f?.entry.message && hasData(f) ? <p className="quiet" data-testid={testId('open', 'files-note')}>{f.entry.message}</p> : null}
        <BundleCard bundle={hasData(f) ? (f?.data?.bundle ?? null) : null} />
        <LeftOut items={hasData(f) ? (f?.data?.left_out ?? []) : []} />
        {list.length ? (
          <div data-dimmed={f?.status === 'stale' ? 'true' : undefined}>
            <HandOff files={list} />
            <AreaFiles files={list} />
          </div>
        ) : null}
      </Section>
    </div>
  )
}

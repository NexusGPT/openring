// Parts: everything to buy or make. The ring stays on the stage; this is the panel on its right: totals and
// export, filter chips, the list (one line per parts-list line), and the charging case's lines in their own
// group. A line opens its card in place; the selection is the address (?part=), so the stage highlights it.
import './parts.css'
import { useEffect, useMemo, useRef, useState } from 'react'
import { StateBanner, parsePartId, testId, type BannerSpec } from '../../contract'
import { PartCard } from '../../components/PartCard'
import { useSearchParams } from '../../app/router'
import { useStageScene } from '../../app/stage-scene'
import { FilterBar } from './FilterBar'
import { Row } from './Row'
import { Totals } from './Totals'
import { isFiltered, linesOf, linesWord, matches, oldDesignBanner, pageIdsOf, parseFilter, writeFilter, type FilterModel } from './model'
import { useParts } from './useParts'

const PARTS_WORDS = { title: 'Everything to buy or make', list: 'The list', totals: 'Totals', none: 'No line matches these filters.', caseGroup: 'The charging case' } as const

function Section({ id, title, aside, children }: { id: string; title: string; aside?: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="sec" aria-labelledby={`parts-${id}`} data-testid={testId('parts', `section-${id}`)}>
      <div className="sec-row">
        <h2 className="label sec-title" id={`parts-${id}`}>{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  )
}

export default function Parts() {
  const d = useParts()
  const [params, setParams] = useSearchParams()
  const [caseOpen, setCaseOpen] = useState(false)
  const listRef = useRef<HTMLUListElement>(null)

  const model = useMemo(() => parseFilter(params), [params])
  const raw = params.get('part')
  const selected = raw && parsePartId(raw) ? raw : null
  const setModel = (m: FilterModel) => setParams(writeFilter(params, m))
  const select = (id: string | null) => {
    const next = new URLSearchParams(params)
    if (id) next.set('part', id)
    else next.delete('part')
    setParams(next)
  }

  const ring = useMemo(() => linesOf(d.parts, 'ring'), [d.parts])
  const caseLines = useMemo(() => linesOf(d.parts, 'case'), [d.parts])
  const pageIds = useMemo(() => pageIdsOf(d.pages, model.page), [d.pages, model.page])
  const shown = useMemo(() => ring.filter((l) => matches(l, model, pageIds)), [ring, model, pageIds])
  const shownCase = useMemo(() => caseLines.filter((l) => matches(l, model, pageIds)), [caseLines, model, pageIds])
  const pageTitle = model.page ? d.pages?.pages.find((p) => p.id === model.page)?.title ?? null : null

  const message = d.partsState && 'entry' in d.partsState ? d.partsState.entry.message : null
  const caseBanner = oldDesignBanner(message, 'case')
  const ringBanner: BannerSpec | null = d.partsState?.status === 'stale' ? { kind: 'stale', basis: d.partsState.entry.basis_version ?? '', current: d.partsState.entry.current_version ?? '' } : oldDesignBanner(message, 'ring')
  const down: BannerSpec | null =
    d.partsState?.status === 'missing' ? { kind: 'missing' } : d.partsState?.status === 'unparsed' ? { kind: 'unparsed', file: d.partsState.entry.source[0] ?? 'design/bom.csv' } : null

  const selectedInCase = !!selected && selected.startsWith('case:')
  const showCase = caseOpen || selectedInCase
  const selectedKnown = !!selected && !!d.parts?.lines.some((l) => l.part_ids.includes(selected))
  // the stage shows the inside while a line is open, so the highlighted object can be seen
  useStageScene({ show: 'internals', explode: selected ? 0.5 : 0 })

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && selected && select(null)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })
  useEffect(() => {
    if (!selected) return
    const el = document.querySelector('[data-testid="parts.card-slot"]') ?? listRef.current?.querySelector('[aria-expanded="true"]')
    const reduce = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches
    el?.scrollIntoView({ block: 'nearest', behavior: reduce ? 'auto' : 'smooth' })
  }, [selected])

  const stamp = [d.version ? `Design ${d.version}` : null, d.updated ? `updated ${d.updated}` : null].filter(Boolean).join(' · ')
  const source = ring[0]?.source.file ?? null
  const rowProps = { selected, onSelect: select, legend: d.parts?.evidence_legend ?? null, notes: d.notes, files: d.files, areaState: d.area?.state ?? null }

  return (
    <div className="pt" data-testid={testId('parts', 'panel')} aria-busy={d.loading} data-dimmed={ringBanner ? 'true' : undefined}>
      <header className="pt-head">
        <h1 className="display">{PARTS_WORDS.title}</h1>
        {stamp ? <p className="label">{stamp}</p> : null}
      </header>

      {down ? <StateBanner route="parts" spec={down} /> : null}
      {!down && ringBanner ? <StateBanner route="parts" spec={ringBanner} /> : null}

      {d.parts ? (
        <>
          <Section id="totals" title={PARTS_WORDS.totals}>
            <Totals parts={d.parts} files={d.files} source={source} />
          </Section>
          <Section
            id="list"
            title={PARTS_WORDS.list}
            aside={<span className="label" data-testid={testId('parts', 'shown')} aria-live="polite">{`${shown.length} of ${linesWord(ring.length)}`}</span>}
          >
            <FilterBar model={model} onChange={setModel} pageTitle={pageTitle} disabled={false} />
            {model.page && d.pages === null ? <p className="pt-note">The wiring pages are not built yet, so this page filter shows no line.</p> : null}
            {selected && !selectedKnown ? <PartCard route="parts" partId={selected} line={null} /> : null}
            {shown.length === 0 ? (
              <p className="pt-empty" data-testid={testId('parts', 'empty')}>{PARTS_WORDS.none}</p>
            ) : (
              <ul className="pt-list" ref={listRef} data-testid={testId('parts', 'list')}>
                {shown.map((l) => (
                  <Row key={`${l.bom}:${l.row}`} line={l} group="ring" banner={null} {...rowProps} />
                ))}
              </ul>
            )}
          </Section>
          {caseLines.length > 0 ? (
            <Section id="case" title={PARTS_WORDS.caseGroup}>
              <button type="button" className="pt-group" aria-expanded={showCase} data-testid={testId('parts', 'case-toggle')} onClick={() => setCaseOpen((v) => !v)}>
                <span>{`${linesWord(d.parts.totals.case.lines)}, not in the ring totals`}</span>
                <span className="label">{showCase ? 'hide' : 'show'}</span>
              </button>
              {showCase ? (
                <div className="pt-case" data-dimmed={caseBanner ? 'true' : undefined}>
                  {caseBanner ? <StateBanner route="parts" spec={caseBanner} /> : null}
                  {shownCase.length === 0 && isFiltered(model) ? (
                    <p className="pt-empty">{PARTS_WORDS.none}</p>
                  ) : (
                    <ul className="pt-list">
                      {shownCase.map((l) => (
                        <Row key={`${l.bom}:${l.row}`} line={l} group="case" banner={null} {...rowProps} />
                      ))}
                    </ul>
                  )}
                </div>
              ) : null}
            </Section>
          ) : null}
        </>
      ) : d.loading ? (
        <div className="pt-skeleton" data-testid={testId('parts', 'loading')} aria-hidden="true">
          <i /><i /><i /><i />
        </div>
      ) : null}
    </div>
  )
}

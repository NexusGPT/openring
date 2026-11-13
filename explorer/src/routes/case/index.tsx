// Case: the charging case in 3D with the ring seated. The case is the shell's stage; this is the panel:
// the key numbers, the lid, the card of the selected part, the parts list and what suppliers are asked.
import './case.css'
import { useEffect, useMemo, useRef, useState } from 'react'
import { StateBanner, banner, testId, type BannerSpec, type RecordId } from '../../contract'
import { useRecord, usePartNotes, type RecordState } from '../../data'
import { useSearchParams } from '../../app/router'
import { useStageScene } from '../../app/stage-scene'
import { PartCard } from '../../components/PartCard'
import { BoardParts } from './BoardParts'
import { Facts } from './Facts'
import { Honest } from './Honest'
import { PartsList } from './PartsList'
import { Supplier } from './Supplier'
import { OPEN_DEG, WORDS, boardOfNode, caseLineOf, caseLines, classWords, countsLine, nodeNames, nodeOf } from './model'

const spec = (id: RecordId, s: RecordState<unknown> | null): BannerSpec | null => {
  if (!s) return null
  if (s.status === 'missing') return { kind: 'missing' }
  if (s.status === 'unparsed') return { kind: 'unparsed', file: s.entry.source[0] ?? id }
  if (s.status === 'stale') return { kind: 'stale', basis: s.entry.basis_version ?? '', current: s.entry.current_version ?? '' }
  return null
}

export default function CaseScreen() {
  const caseRec = useRecord('case')
  const partsRec = useRecord('parts')
  const areas = useRecord('area-states')
  const files = useRecord('files')
  const notes = usePartNotes()
  const [params, setParams] = useSearchParams()
  const [open, setOpen] = useState(false)

  const c = caseRec.state?.data ?? null
  const parts = partsRec.state?.data ?? null
  const hasModel = !!c?.glb
  const names = useMemo(() => JSON.stringify(nodeNames(c, parts)), [c, parts])
  useStageScene({ show: 'case', preset: 'three-quarter', lidOpen: open ? OPEN_DEG : 0, names })

  const card = useRef<HTMLElement | null>(null)
  const lines = useMemo(() => caseLines(c, parts), [c, parts])
  const sel = params.get('part')
  const selId = sel?.startsWith('case:') ? sel : null
  const line = selId ? (parts?.lines.find((l) => l.part_ids.includes(selId)) ?? null) : null
  useEffect(() => {
    if (selId) card.current?.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
  }, [selId])
  const own = caseLineOf(c, selId)
  const board = boardOfNode(c, nodeOf(c, selId)?.name ?? null)
  const objectName = params.get('object')
  const bare = !selId && objectName ? (c?.unlinked_nodes?.find((u) => u.name === objectName) ?? null) : null
  const counts = countsLine(c)
  const select = (id: string | null) => {
    const next = new URLSearchParams(params)
    next.delete('object')
    if (id) next.set('part', id)
    else next.delete('part')
    setParams(next)
  }

  const loading = caseRec.loading || partsRec.loading
  const stale = caseRec.state?.status === 'stale'
  const sp = spec('case', caseRec.state)
  const psp = spec('parts', partsRec.state)
  const caseDown = !!caseRec.state && !c
  const totals = parts?.totals.case
  const reason = stale ? caseRec.state?.entry.message : null

  return (
    <div className="cs" aria-busy={loading} data-testid={testId('case', 'panel')}>
      <header className="cs-head">
        <h1 className="display">{WORDS.title}</h1>
      </header>
      {!loading && sp ? <StateBanner route="case" spec={sp} /> : null}
      {!loading && psp && psp.kind !== 'stale' && !(sp && psp.kind === sp.kind) ? <StateBanner route="case" spec={psp} /> : null}
      {reason ? <p className="cs-reason" data-testid={testId('case', 'stale-reason')}>{reason}</p> : null}
      {c ? (
        <div className="cs-body" data-dimmed={stale ? 'true' : undefined}>
          <section className="cs-sec" data-testid={testId('case', 'numbers')}>
            <h2 className="label">{WORDS.numbers}</h2>
            <Facts facts={c.facts} files={files.state?.data ?? null} />
          </section>
          <section className="cs-sec cs-lidrow">
            <button type="button" className="cs-lid label" data-testid={testId('case', 'lid-toggle')} data-open={open ? 'true' : 'false'} aria-pressed={open} disabled={!hasModel} onClick={() => setOpen((o) => !o)}>
              {open ? WORDS.closeLid : WORDS.openLid}
            </button>
            <p className="cs-hint">{hasModel ? WORDS.lidHint : WORDS.noModel}</p>
          </section>
          {bare ? (
            <section className="cs-sec" data-testid={testId('case', 'bare-node')}>
              <p className="cs-sel-line"><span className="label">{bare.name.replace(/_/g, ' ')}</span><span>{bare.text}</span></p>
            </section>
          ) : null}
          {selId ? (
            <section ref={card} className="cs-sec" data-testid={testId('case', 'selected')}>
              {line ? (
                <p className="cs-sel-line" data-testid={testId('case', 'selected-line')}>
                  <span className="label">{WORDS.listLine}</span>
                  <span>{`${line.function ?? line.item} \u00b7 ${line.refs.join(' ')}`}</span>
                </p>
              ) : null}
              {own ? (
                <p className="cs-hint" data-testid={testId('case', 'selected-class')} data-class={own.class}>
                  {`${classWords(c, own)}${own.reason ? `: ${own.reason}` : ''}`}
                </p>
              ) : null}
              <PartCard
                route="case"
                partId={selId}
                line={line}
                note={notes.state?.data?.notes[selId] ?? null}
                legend={parts?.evidence_legend ?? null}
                files={files.state?.data ?? null}
                areaState={areas.state?.data?.areas.find((a) => a.id === 'case')?.state ?? null}
                banner={sp?.kind === 'stale' ? sp : null}
              />
              <button type="button" className="cs-clear" onClick={() => select(null)}>Close part card</button>
            </section>
          ) : null}
          {board && !bare ? <BoardParts board={board} selected={selId} onSelect={select} /> : null}
          <section className="cs-sec">
            <h2 className="label">
              {WORDS.parts}
              {totals ? <span className="cs-count" data-testid={testId('case', 'parts-count')}>{` · ${totals.lines} ${WORDS.linesOf} · ${totals.parts} ${WORDS.partsOf}`}</span> : null}
            </h2>
            {counts ? <p className="cs-hint" data-testid={testId('case', 'counts-line')}>{counts}</p> : null}
            {c.unlinked_nodes?.length ? (
              <p className="cs-hint" data-testid={testId('case', 'unlinked-nodes')}>{`${c.unlinked_nodes.length} solids of the model have no parts-list line: ${c.unlinked_nodes.map((u) => u.name).join(', ')}`}</p>
            ) : null}
            <PartsList lines={lines} selected={selId} onSelect={select} classOf={(l) => { const k = caseLineOf(c, l.part_ids[0] ?? null); return k ? classWords(c, k) : null }} />
          </section>
          <Honest model={c.model ?? null} refit={c.refit ?? null} />
          {c.supplier_items.length ? (
            <section className="cs-sec">
              <h2 className="label">{WORDS.supplier}</h2>
              <Supplier items={c.supplier_items} />
            </section>
          ) : null}
        </div>
      ) : null}
      {!loading && caseDown && !hasModel && sp?.kind === 'stale' ? <p className="cs-hint">{banner(sp).sentence}</p> : null}
    </div>
  )
}

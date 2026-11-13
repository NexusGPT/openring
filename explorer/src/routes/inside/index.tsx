// Inside: what is in the ring. The ring (3D, in the shell's stage) opens with one control; a part is chosen on
// the stage, in the layer list or by search. A made-to-drawing part also slides its drawing up under the ring.
import './inside.css'
import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from '../../app/router'
import { FILES_TO } from '../../app/route-names'
import { useStageScene } from '../../app/stage-scene'
import { PartCard } from '../../components/PartCard'
import { StateBanner, WORDS, parsePartId, testId } from '../../contract'
import { DrawingStrip, type StripData } from './DrawingStrip'
import { LayerList } from './LayerList'
import { firstSize, isMadeToDrawing, makerFiles } from './makerFiles'
import { layerOfPart, layerRows, lineOf, objectsOfLayer, ringLines, type ObjectRow } from './model'
import { Presence, useAnimatedValue } from './motion'
import { BoughtPanel, MadePanel } from './PartPanel'
import { PartSearch } from './PartSearch'
import { StageOverlay } from './StageOverlay'
import { useInside } from './useInside'

function Section({ title, id, children, aside }: { title: string; id: string; children: React.ReactNode; aside?: React.ReactNode }) {
  return (
    <section className="sec" aria-labelledby={`inside-${id}`} data-testid={testId('inside', `section-${id}`)}>
      <div className="sec-row">
        <h2 className="label sec-title" id={`inside-${id}`}>{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  )
}

/** An object of the model that no parts-list line names: it says so in words. */
function UnlinkedObject({ name }: { name: string }) {
  return (
    <article className="in-unlinked" data-testid={testId('inside', 'part-card')} data-object={name}>
      <div className="label">Object</div>
      <h3 className="display">{name.replace(/[_-]+/g, ' ')}</h3>
      <p className="in-none" data-testid={testId('inside', 'part-card-no-line')}>{WORDS.noPartsLine}</p>
    </article>
  )
}

export default function Inside() {
  const d = useInside()
  const [params, setParams] = useSearchParams()
  const [explode, setExplode, animateExplode] = useAnimatedValue(0)
  const [isolated, setIsolated] = useState<string | null>(null)
  const [pick, setPick] = useState<{ id: string; size: number } | null>(null)

  const rawId = params.get('part')
  const selectedId = rawId && parsePartId(rawId) ? rawId : null
  const objectName = selectedId ? null : params.get('object')
  const lines = useMemo(() => ringLines(d.parts), [d.parts])
  const rows = useMemo(() => layerRows(d.placements), [d.placements])
  const partsCount = rows.reduce((n, r) => n + r.count, 0)
  const objects = useMemo(
    () => (isolated ? objectsOfLayer(isolated, d.placements, d.parts, d.notes, d.ringModel) : []),
    [isolated, d.placements, d.parts, d.notes, d.ringModel],
  )

  // the stage's hover tag: each object by its parts-list item
  const names = useMemo(
    () => JSON.stringify(Object.fromEntries((d.placements?.placements ?? []).flatMap((p) => {
      const o = objectsOfLayer(p.layer, d.placements, d.parts, d.notes, d.ringModel).find((x) => x.name === p.name)
      return o ? [[p.name, o.label]] : []
    }))),
    [d.placements, d.parts, d.notes, d.ringModel],
  )
  useStageScene({ show: 'internals', explode, isolatedLayer: isolated, names })

  const choose = (id: string | null, object?: string) => {
    const next = new URLSearchParams(params)
    next.delete('part')
    next.delete('object')
    if (id) next.set('part', id)
    else if (object) next.set('object', object)
    setParams(next)
  }
  const clear = () => choose(null)
  const fromSearch = (id: string) => {
    // a part found by name may sit inside the body: show its layer alone so the highlight can be seen
    const layer = layerOfPart(id, d.placements, d.notes, d.ringModel)
    if (layer) setIsolated(layer)
    choose(id)
  }
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null
      if (e.key === 'Escape' && !(t && /input|textarea/i.test(t.tagName))) clear()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })
  // a chosen part lives inside the ring: the ring opens (eased) when it is still closed
  useEffect(() => {
    if ((selectedId || objectName) && explode < 0.5) animateExplode(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId, objectName])
  const isolate = (id: string | null) => {
    setIsolated(id)
    if (id && explode < 0.5) animateExplode(1)
  }
  const toggleRing = () => animateExplode(explode > 0.5 ? 0 : 1)

  const line = selectedId ? lineOf(d.parts, selectedId) : null
  const made = isMadeToDrawing(line)
  const set = useMemo(() => makerFiles(d.files, line), [d.files, line])
  const ringSize = pick && pick.id === selectedId && set.sizes.includes(pick.size) ? pick.size : firstSize(set)
  const note = selectedId ? (d.notes?.[selectedId] ?? null) : null
  const nothingYet = !d.loading && !d.ringModel && !d.parts
  const in3d = selectedId ? layerOfPart(selectedId, d.placements, d.notes, d.ringModel) : null
  const layerLabel = in3d ? (d.placements?.layers.find((l) => l.id === in3d)?.label ?? in3d) : null
  const tagName = line?.item ?? (selectedId ? (note?.what ?? selectedId) : objectName ? objectName.replace(/[_-]+/g, ' ') : '')
  const strip: StripData | null = line && made ? { name: line.item, sizes: line.size_mm, set, ringSize } : null

  const stamp = [d.version ? `Design ${d.version}` : null, d.updated ? `updated ${d.updated}` : null].filter(Boolean).join(' · ')
  const cardKey = selectedId ?? (objectName ? `object:${objectName}` : null)
  const fromList = (o: ObjectRow) => choose(o.partId, o.name)

  const detail = selectedId ? (
    line ? (
      made ? (
        <MadePanel id={selectedId} line={line} note={note} files={d.files} set={set} ringSize={ringSize} />
      ) : (
        <BoughtPanel id={selectedId} line={line} note={note} legend={d.parts?.evidence_legend ?? null} files={d.files} areaState={d.insideArea?.state ?? null} />
      )
    ) : (
      <PartCard route="inside" partId={selectedId} line={null} note={note} legend={null} files={d.files} areaState={d.insideArea?.state ?? null} />
    )
  ) : objectName ? (
    <UnlinkedObject name={objectName} />
  ) : null

  return (
    <div className="in" data-testid={testId('inside', 'panel')} data-dimmed={d.stale ? 'true' : undefined} aria-busy={d.loading}>
      <header className="in-head">
        <h1 className="display">What is in the ring</h1>
        {stamp ? <p className="label">{stamp}</p> : null}
        {rows.length > 0 && (
          <p className="in-count" data-testid={testId('inside', 'count')}>
            {`${partsCount} parts drawn in 3D, in ${rows.length} layers. Pick a layer or a part, or open the ring.`}
          </p>
        )}
      </header>
      {d.banners.map((b) => (
        <StateBanner key={JSON.stringify(b)} route="inside" spec={b} />
      ))}
      <Presence k={cardKey ?? 'list'}>
        {cardKey ? (
          <div className="in-frame" data-frame="part">
            <button type="button" className="in-back" data-testid={testId('inside', 'card-close')} onClick={clear}>← All layers</button>
            {detail}
          </div>
        ) : (
          <div className="in-frame" data-frame="list">
            <Section title="Find a part" id="find">
              <PartSearch lines={lines} notes={d.notes} onSelect={fromSearch} disabled={!d.parts} />
              <p className="in-hint muted" data-testid={testId('inside', 'hint')}>
                {nothingYet ? 'Nothing to open yet.' : 'Click a part in the ring, pick a layer below, or search by name.'}
              </p>
            </Section>
            <LayerList
              rows={[...rows].reverse()}
              total={partsCount}
              isolated={isolated}
              onIsolate={isolate}
              objects={objects}
              selectedId={selectedId}
              onPick={fromList}
            />
            <Link to={FILES_TO} className="in-maker" data-testid={testId('inside', 'link-for-manufacturer')}>For a manufacturer →</Link>
          </div>
        )}
      </Presence>
      <StageOverlay
        split={Boolean(strip)}
        ringOpen={explode > 0.5}
        onToggle={toggleRing}
        onAnimate={animateExplode}
        value={explode}
        onValue={setExplode}
        disabled={!d.ringModel}
        tag={cardKey ? { layer: layerLabel, name: tagName } : null}
        onClear={clear}
      >
        <DrawingStrip open={Boolean(strip)} data={strip} onSize={(n) => selectedId && setPick({ id: selectedId, size: n })} />
      </StageOverlay>
    </div>
  )
}

// Board: the circuit boards. A picker chooses the ring board, a band circuit (and its ring size) or a case board; the banner gives
// the board's state from its rules check; the plan shows the outline and every part on each face over the copper layers, one at a
// time or stacked; a click on a part opens its card. Data from before the list of boards falls back to the single ring plan.
import './board.css'
import { useMemo, useRef } from 'react'
import { PartCard } from '../../components/PartCard'
import { SvgViewer, type SvgViewerHandle } from '../../components/SvgViewer'
import { StateBanner, WORDS, parsePartId, testId, type BoardFiles } from '../../contract'
import { dataUrl } from '../../data'
import { findBoxFocus } from './focus'
import { useRefit, useSvgText, viewBoxOfText } from '../electronics/focus'
import { useWidePanel } from '../electronics/useWide'
import { useSearchParams } from '../../app/router'
import { useStageScene } from '../../app/stage-scene'
import { useScrollIn } from '../electronics/useScrollIn'
import { PlacedList } from './PlacedList'
import { PlanSvg } from './PlanSvg'
import { SideToggle } from './SideToggle'
import { BoardPicker } from './BoardPicker'
import { ConnectionsOfBoard } from './ConnectionsOfBoard'
import { LayerToggle } from './LayerToggle'
import { StateLine } from './StateLine'
import {
  boardLayerId, countSide, groupsOf, labelOf as wordsOf, layerChoice, layersShown, lineOf, mm, outsideCount, partIdOf, pickEntry, planOf,
  type Mode, type Placement,
} from './model'
import { useBoard } from './useBoard'

const MODE_IDS: readonly string[] = ['top', 'bottom', 'both']

function Facts({ rows }: { rows: [string, string][] }) {
  return (
    <dl className="bd-facts" data-testid={testId('board', 'facts')}>
      {rows.map(([k, v]) => (
        <div key={k}><dt>{k}</dt><dd>{v}</dd></div>
      ))}
    </dl>
  )
}

export default function Board() {
  const d = useBoard()
  useWidePanel()
  const [params, setParams] = useSearchParams()
  const modeParam = params.get('side')
  const mode = (MODE_IDS.includes(modeParam ?? '') ? modeParam : 'both') as Mode
  const groups = useMemo(() => groupsOf(d.board?.boards), [d.board])
  const group = groups.find((g) => g.id === params.get('board')) ?? groups[0] ?? null
  const entry = group ? pickEntry(group, params.get('size')) : null
  // the 3D layer that holds the circuit board is the ring board's; another board does not isolate it
  const layer = useMemo(() => (!group || group.id === 'ring' ? boardLayerId(d.board, d.placements, d.notes) : null), [d.board, d.placements, d.notes, group])
  useStageScene({ show: 'internals', explode: 0.4, isolatedLayer: layer })

  const rawPart = params.get('part')
  const partParam = rawPart && parsePartId(rawPart) ? rawPart : null
  const objectParam = partParam ? null : params.get('object')
  // the plan of the shown board: its own entry; the single ring plan for data without the list, or while the ring board file is not there
  const plan: BoardFiles | null = entry && (entry.file || entry.placements.length > 0) ? planOf(entry) : !group || group.id === 'ring' ? d.board : null
  const placed = plan?.placements ?? []
  const current = placed.find((p) => (partParam ? partIdOf(p, d.notes) === partParam : p.name === objectParam)) ?? null
  const label = (p: Placement) => wordsOf(p, d.parts, d.notes)
  const refOf = (p: Placement) => { const id = partIdOf(p, d.notes); return id ? id.slice(id.indexOf(':') + 1) : p.name }
  const picture = params.get('view') === 'file' ? 'drawing' : 'plan'

  const write = (edit: (n: URLSearchParams) => void) => {
    const n = new URLSearchParams(params)
    edit(n)
    setParams(n)
  }
  const setBoard = (id: string) => write((n) => { n.set('board', id); n.delete('size'); n.delete('part'); n.delete('object'); n.delete('layer'); n.delete('view') })
  const setSize = (label: string) => write((n) => { n.set('size', label); n.delete('part'); n.delete('object') })
  const setLayer = (c: string) => write((n) => (entry && c === entry.layers[0]?.id ? n.delete('layer') : n.set('layer', c)))
  const select = (p: Placement) =>
    write((n) => {
      const same = current?.name === p.name
      n.delete('part')
      n.delete('object')
      if (same) return
      const id = partIdOf(p, d.notes)
      if (id) n.set('part', id)
      else n.set('object', p.name)
    })
  const setMode = (m: Mode) => write((n) => (m === 'both' ? n.delete('side') : n.set('side', m)))

  const cardId = partParam ?? (current ? partIdOf(current, d.notes) : null)
  const b = plan
  const choice = layerChoice(entry, params.get('layer'))
  const shown = layersShown(entry && plan !== d.board ? entry : null, choice)
  const legacyPic = !entry || plan === d.board ? (d.board ? (mode === 'bottom' ? d.board.svg.bottom : d.board.svg.top) : null) : null
  const pictures = [...shown.flatMap((l) => (l.svg ? [l.svg] : [])), ...(legacyPic ? [legacyPic] : [])]
  const filePic = pictures[pictures.length - 1] ?? null
  const showFile = !!filePic && picture === 'drawing'
  const outside = b ? outsideCount(b) : 0
  const svgText = useSvgText(showFile && filePic ? dataUrl(filePic) : null)
  const vb = viewBoxOfText(svgText)
  const picBox = useRef<HTMLElement>(null)
  const viewer = useRef<SvgViewerHandle>(null)
  useRefit(picBox, viewer)
  const focus = findBoxFocus(b, current, vb)
  const empty = !d.loading && !b
  const cardBox = useRef<HTMLElement>(null)
  useScrollIn(cardBox, current?.name ?? cardId)
  const stamp = [d.version ? `Design ${d.version}` : null, d.updated ? `updated ${d.updated}` : null].filter(Boolean).join(' · ')

  const boardsMissing = !!d.board && !d.board.boards
  const facts: [string, string][] = b
    ? [
        ...(b.outline ? [['Board size', `${mm(b.outline.w)} × ${mm(b.outline.h)} mm`] as [string, string]] : []),
        ['Parts placed', `${b.placements.length} · ${countSide(b, 'top')} on top, ${countSide(b, 'bottom')} on the bottom`],
        ...(entry && entry.layers.length > 0 ? [['Copper layers', `${entry.layers.length} · ${entry.layers.map((l) => l.label.toLowerCase()).join(', ')}`] as [string, string]] : []),
        ...((b.notches?.length ?? 0) > 0 ? [['Cut-outs', String(b.notches?.length)] as [string, string]] : []),
        ...(outside > 0 ? [['Not on the board yet', `${outside} ${outside === 1 ? 'part sits' : 'parts sit'} outside the outline`] as [string, string]] : []),
      ]
    : []
  const layerWords = shown.length > 1 ? 'all copper layers' : shown[0]?.label.toLowerCase() ?? 'no copper'

  return (
    <div className="bd" data-testid={testId('board', 'panel')} data-dimmed={d.stale ? 'true' : undefined} aria-busy={d.loading}>
      <header className="bd-head">
        <h1 className="display">The circuit boards</h1>
        {stamp ? <p className="label">{stamp}</p> : null}
      </header>
      {group && entry ? (
        <div className="bd-top">
          <BoardPicker groups={groups} group={group} size={entry.size_label} onGroup={setBoard} onSize={setSize} />
          <p className="bd-what muted" data-testid={testId('board', 'what')}>{entry.what}</p>
        </div>
      ) : null}
      <div className="bd-banners">{d.banners.map((x) => <StateBanner key={JSON.stringify(x)} route="board" spec={x} />)}</div>

      {empty && !entry ? (
        <p className="bd-none muted bd-nothing" data-testid={testId('board', 'nothing')}>Nothing to show yet.</p>
      ) : (
        <>
          {boardsMissing && (
            <p className="bd-none muted" data-testid={testId('board', 'boards-none')}>The list of boards is not in the data yet; only the ring board plan is shown. Run <code>npm run collect</code>.</p>
          )}
          {entry && <StateLine entry={entry} files={d.files} />}
          {b ? (
            <>
              <Facts rows={facts} />
              <div className="bd-row bd-controls">
                <SideToggle mode={mode} onChange={setMode} />
                {entry && plan !== d.board ? <LayerToggle entry={entry} choice={choice} onChange={setLayer} /> : null}
                {filePic ? (
                  <div className="bd-toggle" role="group" aria-label="Picture">
                    {(['plan', 'drawing'] as const).map((v) => (
                      <button key={v} type="button" aria-pressed={picture === v} data-testid={testId('board', `view-${v}`)} onClick={() => write((n) => (v === 'plan' ? n.delete('view') : n.set('view', 'file')))}>
                        {v === 'plan' ? 'Plan' : 'Zoom the file'}
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
              <section className="bd-plan-wrap" ref={picBox} aria-label="Board picture">
                {showFile && filePic ? (
                  <SvgViewer
                    ref={viewer} route="board" src={dataUrl(filePic)}
                    label={entry && plan !== d.board ? `${entry.title}${entry.size_label ? `, ${entry.size_label}` : ''}: ${layerWords}` : `Circuit board file, ${mode === 'bottom' ? 'bottom' : 'top'} side`}
                    viewBox={vb ?? undefined} focus={focus}
                  />
                ) : (
                  <PlanSvg board={b} mode={mode} selected={current?.name ?? null} labelOf={label} onSelect={select} underlays={pictures.map((u) => dataUrl(u))} />
                )}
                {entry && plan !== d.board && shown.length > 0 && <p className="label bd-caption" data-testid={testId('board', 'caption')}>{`${layerWords}, seen from above`}</p>}
              </section>
              {group ? <ConnectionsOfBoard map={d.connections} group={group.id} /> : null}
              <PlacedList placements={placed} mode={mode} selected={current?.name ?? null} labelOf={label} refOf={refOf} onSelect={select} />
              {(cardId || current) && (
                <section className="bd-card" ref={cardBox} aria-label="The part" data-testid={testId('board', 'card-slot')} key={current?.name ?? cardId}>
                  {cardId ? (
                    <PartCard
                      route="board" partId={cardId} line={lineOf(d.parts, cardId)} note={d.notes?.[cardId] ?? null}
                      legend={d.parts?.evidence_legend ?? null} files={d.files} areaState={d.area?.state ?? null}
                    />
                  ) : current ? (
                    <article className="bd-unlinked" data-testid={testId('board', 'part-card')} data-object={current.name}>
                      <div className="label">Object</div>
                      <h3 className="display">{label(current)}</h3>
                      <p className="bd-none muted" data-testid={testId('board', 'part-card-no-line')}>{WORDS.noPartsLine}</p>
                    </article>
                  ) : null}
                </section>
              )}
            </>
          ) : group ? (
            <>
              <p className="bd-none muted" data-testid={testId('board', 'no-plan')}>This board has nothing to draw yet. The other boards still show.</p>
              <ConnectionsOfBoard map={d.connections} group={group.id} />
            </>
          ) : null}
        </>
      )}
    </div>
  )
}

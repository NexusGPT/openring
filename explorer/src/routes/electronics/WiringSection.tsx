// The connection map below the wiring diagram: the boards and parts as a map or a list, and the chosen connection in words.
import { useEffect, useMemo, useRef } from 'react'
import { testId, type AreaState, type Files, type Parts } from '../../contract'
import { ConnectionDetail } from './ConnectionDetail'
import { ConnectionList } from './ConnectionList'
import { ConnectionMap } from './ConnectionMap'
import { isOpen, productCountWords, type ConnectionMap as WiringMap } from '../../components/wiring/wiringModel'
import type { Notes } from './model'

export type WiringView = 'map' | 'list'

interface Props {
  map: WiringMap | null
  view: WiringView
  selected: string | null
  part: string | null
  parts: Parts | null
  notes: Notes | null
  files: Files | null
  areaState: AreaState | null
  /** group ids of the boards the Board screen can show */
  boardGroups: readonly string[]
  loading: boolean
  onView: (v: WiringView) => void
  onSelect: (id: string | null) => void
  onPart: (id: string | null) => void
}

export function WiringSection({ map, view, selected, part, parts, notes, files, areaState, boardGroups, loading, onView, onSelect, onPart }: Props) {
  const detailBox = useRef<HTMLDivElement>(null)
  const conn = useMemo(() => map?.connections.find((c) => c.id === selected) ?? null, [map, selected])
  // a connection chosen by a link (from the Board screen) opens at the top of the view; one chosen on the map keeps the map in sight
  const first = useRef(selected !== null)
  const connId = conn?.id ?? null
  useEffect(() => {
    if (!connId) return
    const calm = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
    detailBox.current?.scrollIntoView?.({ behavior: calm ? 'auto' : 'smooth', block: first.current ? 'start' : 'nearest' })
    first.current = false
  }, [connId])
  const nOpen = map ? map.connections.filter(isOpen).length : 0
  return (
    <section className="el-conns" aria-labelledby="el-conns-h" data-testid={testId('electronics', 'connections')}>
      <div className="el-sec-row">
        <h2 className="display el-conns-title" id="el-conns-h">What is joined to what</h2>
        {map && map.connections.length > 0 && (
          <div className="el-toggle" role="group" aria-label="Map or list">
            {(['map', 'list'] as const).map((v) => (
              <button key={v} type="button" aria-pressed={view === v} onClick={() => onView(v)} data-testid={testId('electronics', `conn-view-${v}`)}>
                {v === 'map' ? 'Map' : 'List'}
              </button>
            ))}
          </div>
        )}
      </div>

      {!map ? (
        loading ? null : <p className="el-none muted" data-testid={testId('electronics', 'conn-none')}>The connection map is not in the data yet. Run <code>npm run collect</code>.</p>
      ) : (
        <>
          <p className="label" data-testid={testId('electronics', 'conn-count')}>
            {`${map.connections.length} connections`}
            {nOpen > 0 ? ` · ${nOpen} not drawn in a design file` : ''}
            {map.file_time ? ` · list of ${map.file_time}` : ''}
          </p>
          <p className="label" data-testid={testId('electronics', 'conductor-total')}>{productCountWords(map.conductor_file)}</p>
          {map.note && <p className="el-none el-conn-note" role="status" data-testid={testId('electronics', 'conn-note')}>{map.note}</p>}
          {map.connections.length === 0 ? (
            <p className="el-none muted">The list holds no connection.</p>
          ) : view === 'list' ? (
            <ConnectionList map={map} selected={selected} onSelect={onSelect} />
          ) : (
            <ConnectionMap map={map} selected={selected} onSelect={onSelect} />
          )}
          <div ref={detailBox}>
            {conn ? (
              <ConnectionDetail
                map={map} conn={conn} part={part} parts={parts} notes={notes} files={files} areaState={areaState}
                hasBoard={(g) => boardGroups.includes(g)} onPart={onPart}
              />
            ) : map.connections.length > 0 ? (
              <p className="el-none muted" data-testid={testId('electronics', 'conn-hint')}>Choose a connection to see its two ends, what it carries, how it is made and which file proves it.</p>
            ) : null}
          </div>
        </>
      )}
    </section>
  )
}

// The connection map: boards and off-board parts as nodes, every joint between them as a line with a small pill.
// A click on a pill (or its line) chooses the connection. A joint no design file draws is dashed and carries the accent.
import { useMemo, useState } from 'react'
import { testId } from '../../contract'
import { edgesOf, isOpen, layoutNodes, shiftOf, type ConnectionMap as WiringMap } from '../../components/wiring/wiringModel'

interface Props {
  map: WiringMap
  selected: string | null
  onSelect: (id: string) => void
}

export function ConnectionMap({ map, selected, onSelect }: Props) {
  const [hover, setHover] = useState<string | null>(null)
  const layout = useMemo(() => layoutNodes(map), [map])
  const edges = useMemo(() => edgesOf(map), [map])
  const byId = useMemo(() => new Map(map.connections.map((c) => [c.id, c] as const)), [map.connections])
  const active = hover ?? selected
  const chosen = active ? byId.get(active) : undefined
  const ends = new Set(chosen ? chosen.ends.map((e) => e.node) : [])
  return (
    <div
      className="el-map" style={{ '--levels': layout.levels, '--across': layout.across } as React.CSSProperties}
      data-testid={testId('electronics', 'conn-map')} onMouseLeave={() => setHover(null)}
    >
      <svg className="el-map-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        {edges.map((e) => {
          const a = layout.places.get(e.a)
          const b = layout.places.get(e.b)
          const c = byId.get(e.id)
          if (!a || !b || !c) return null
          const dy = shiftOf(e.k, e.m)
          return (
            <path
              key={e.id} d={`M ${a.x + dy} ${a.y} L ${b.x + dy} ${b.y}`} className="el-map-line"
              data-open={isOpen(c) || undefined} data-lit={e.id === active || undefined}
              vectorEffect="non-scaling-stroke" data-testid={testId('electronics', 'conn-line')} data-conn={e.id}
              onClick={() => onSelect(e.id)} onMouseEnter={() => setHover(e.id)}
            />
          )
        })}
      </svg>
      {map.nodes.map((n) => {
        const p = layout.places.get(n.id)
        const count = map.connections.filter((c) => c.ends.some((e) => e.node === n.id)).length
        return (
          <div
            key={n.id} className="el-node" data-kind-node={n.kind} data-lit={ends.has(n.id) || undefined}
            style={{ left: `${p?.x ?? 50}%`, top: `${p?.y ?? 50}%` }}
            data-testid={testId('electronics', 'conn-node')} data-node={n.id} role="group" aria-label={`${n.label}, ${count} connections`}
          >
            <span className="el-node-name">{n.label}</span>
            <span className="el-node-meta label">{[n.kind === 'board' ? 'board' : n.scope, `${count} ${count === 1 ? 'link' : 'links'}`].filter(Boolean).join(' · ')}</span>
          </div>
        )
      })}
      {edges.map((e) => {
        const a = layout.places.get(e.a)
        const b = layout.places.get(e.b)
        const c = byId.get(e.id)
        if (!a || !b || !c) return null
        return (
          <button
            key={e.id} type="button" className="el-pill" aria-pressed={selected === e.id} data-open={isOpen(c) || undefined}
            style={{ left: `${(a.x + b.x) / 2 + shiftOf(e.k, e.m)}%`, top: `${(a.y + b.y) / 2}%` }}
            data-testid={testId('electronics', 'conn-pill')} data-conn={e.id} aria-label={`Connection ${e.id}${isOpen(c) ? ', not drawn in any file' : ''}`}
            onClick={() => onSelect(e.id)} onMouseEnter={() => setHover(e.id)} onFocus={() => setHover(e.id)} onBlur={() => setHover(null)}
          >
            {e.id}
          </button>
        )
      })}
    </div>
  )
}

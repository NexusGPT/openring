// The circuit as blocks and their links. A block is a button; the lines are the links between blocks.
// The block with most links is in the middle, the others stand in two columns beside it.
import { useMemo, useState } from 'react'
import { testId } from '../../contract'
import { layoutBlocks, type Block, type Link, type Page, type Placed } from './model'

interface Props {
  blocks: readonly Block[]
  links: readonly Link[]
  selected: string | null
  pageOf: (b: Block) => Page | null
  onSelect: (id: string) => void
}

// where a line meets a block, in percent of the diagram width
const EDGE = { left: 34, mid: 50, right: 66 } as const
const HUB_EDGE = { left: 38, right: 62 } as const

function pathOf(a: Placed, b: Placed): string {
  if (a.col === 'mid' || b.col === 'mid') {
    const hub = a.col === 'mid' ? a : b
    const o = a.col === 'mid' ? b : a
    const side = o.col === 'left' ? 'left' : 'right'
    return `M ${HUB_EDGE[side]} ${hub.y} L ${EDGE[side]} ${o.y}`
  }
  if (a.col !== b.col) return `M ${EDGE[a.col]} ${a.y} L ${EDGE[b.col]} ${b.y}`
  const out = a.col === 'left' ? EDGE.left + 9 : EDGE.right - 9
  return `M ${EDGE[a.col]} ${a.y} Q ${out} ${(a.y + b.y) / 2} ${EDGE[b.col]} ${b.y}`
}

export function BlockDiagram({ blocks, links, selected, pageOf, onSelect }: Props) {
  const [hover, setHover] = useState<string | null>(null)
  const { placed, rows } = useMemo(() => layoutBlocks(blocks, links), [blocks, links])
  const at = (id: string) => placed.find((p) => p.id === id)
  const focus = hover ?? selected
  const lit = (l: Link) => focus !== null && (l.from === focus || l.to === focus)
  return (
    <div className="el-diagram" style={{ '--rows': rows } as React.CSSProperties} data-testid={testId('electronics', 'diagram')} onMouseLeave={() => setHover(null)}>
      <svg className="el-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        {links.map((l) => {
          const a = at(l.from)
          const b = at(l.to)
          if (!a || !b) return null
          return (
            <path
              key={`${l.from}>${l.to}`} d={pathOf(a, b)} className="el-line" data-lit={lit(l) || undefined}
              style={{ strokeWidth: 1 + Math.min(l.nets.length, 4) * 0.4 }} vectorEffect="non-scaling-stroke"
              data-testid={testId('electronics', 'link')} data-from={l.from} data-to={l.to} data-nets={l.nets.length}
            />
          )
        })}
      </svg>
      {blocks.map((b) => {
        const p = at(b.id)
        const page = pageOf(b)
        return (
          <button
            key={b.id} type="button" className="el-block" title={b.label} data-col={p?.col} style={{ top: `${p?.y ?? 50}%` }}
            aria-pressed={selected === b.id}
            data-testid={testId('electronics', 'block')} data-block={b.id}
            onClick={() => onSelect(b.id)} onMouseEnter={() => setHover(b.id)} onFocus={() => setHover(b.id)} onBlur={() => setHover(null)}
          >
            <span className="el-block-name">{b.label}</span>
            <span className="el-block-meta label">
              {`${b.part_ids.length} ${b.part_ids.length === 1 ? 'part' : 'parts'}${page ? ` · page ${page.number}` : ''}`}
            </span>
          </button>
        )
      })}
    </div>
  )
}

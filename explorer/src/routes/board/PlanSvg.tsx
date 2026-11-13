// The placement plan, drawn from the board record's numbers: outline, cut-outs, every part where it is planned
// to sit. React text and shapes only; nothing from the bundle is parsed as markup.
import { useState } from 'react'
import { testId } from '../../contract'
import { shows, topOf, left, viewBoxOf, yDown, type Mode, type Placement } from './model'
import type { BoardFiles } from '../../contract'

interface Props {
  board: BoardFiles
  mode: Mode
  selected: string | null
  labelOf: (p: Placement) => string
  onSelect: (p: Placement) => void
  /** the board pictures (bundle URLs) drawn under the marks, on the outline; several are stacked */
  underlays?: readonly string[]
}

export function PlanSvg({ board, mode, selected, labelOf, onSelect, underlays = [] }: Props) {
  const [hover, setHover] = useState<string | null>(null)
  const vb = viewBoxOf(board)
  if (!vb) return null
  const down = yDown(board)
  const top = (b: { x: number; y: number; w: number; h: number }) => topOf(b, down)
  const o = board.outline
  const note = hover ?? selected
  const named = board.placements.find((p) => p.name === note)
  return (
    <svg
      className="bd-plan" viewBox={vb.join(' ')} role="group" aria-label="Placement plan of the circuit board, seen from above"
      data-testid={testId('board', 'plan')} data-underlay={underlays.length > 0 ? 'true' : undefined} data-stacked={underlays.length > 1 ? 'true' : undefined} onMouseLeave={() => setHover(null)}
    >
      {o && underlays.map((u) => <image key={u} href={u} x={left(o)} y={top(o)} width={o.w} height={o.h} preserveAspectRatio="none" data-testid={testId('board', 'plan-picture')} />)}
      {o && <rect className="bd-outline" x={left(o)} y={top(o)} width={o.w} height={o.h} data-testid={testId('board', 'outline')} />}
      {(board.notches ?? []).map((n) => (
        <g key={n.name} data-testid={testId('board', 'notch')} data-notch={n.name}>
          <rect className="bd-notch" data-known={n.position_known} x={left(n)} y={top(n)} width={n.w} height={n.h} />
          <title>{`${n.name.replace(/[_-]+/g, ' ')}${n.position_known ? '' : ' (position not stated in the design)'}`}</title>
        </g>
      ))}
      {/* a click area of at least 1.6 mm round each small part, drawn UNDER every part so it never covers a neighbour */}
      {board.placements.filter((p) => shows(mode, p.side) && (p.w < 1.6 || p.h < 1.6)).map((p) => (
        <rect
          key={p.name} className="bd-hit" aria-hidden="true" data-hit={p.name}
          x={left(p) - Math.max(0, 1.6 - p.w) / 2} y={top(p) - Math.max(0, 1.6 - p.h) / 2} width={Math.max(p.w, 1.6)} height={Math.max(p.h, 1.6)}
          onClick={() => onSelect(p)} onMouseEnter={() => setHover(p.name)}
        />
      ))}
      {drawOrder(board.placements, selected).map((p) => (
        <g
          key={p.name} className="bd-part" role="button" tabIndex={shows(mode, p.side) ? 0 : -1} aria-label={labelOf(p)}
          aria-pressed={selected === p.name} data-hidden={!shows(mode, p.side) || undefined}
          data-testid={testId('board', 'plan-mark')} data-part={p.name} data-side={p.side}
          onClick={() => onSelect(p)} onMouseEnter={() => setHover(p.name)} onFocus={() => setHover(p.name)} onBlur={() => setHover(null)}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(p) } }}
        >
          <rect x={left(p)} y={top(p)} width={p.w} height={p.h} />
          <title>{labelOf(p)}</title>
        </g>
      ))}
      {named && shows(mode, named.side) && <Tag part={named} text={labelOf(named)} vb={vb} y={top(named)} />}
    </svg>
  )
}

/** The name of the hovered or chosen part, sized to the drawing and kept inside it. */
function Tag({ part, text, vb, y: topY }: { part: Placement; text: string; vb: readonly [number, number, number, number]; y: number }) {
  const size = vb[2] * 0.034
  const half = (text.length * size * 0.55) / 2
  const x = Math.min(Math.max(part.x, vb[0] + half + 0.5), vb[0] + vb[2] - half - 0.5)
  const above = topY - size * 0.5
  const y = above < vb[1] + size ? topY + part.h + size * 1.1 : above
  return <text className="bd-tag" x={x} y={y} fontSize={size} textAnchor="middle" data-testid={testId('board', 'plan-tag')}>{text}</text>
}

/** Big parts first, small ones on top, the chosen one last: a 0.5 mm part is never covered by a neighbour's click area. */
function drawOrder(list: readonly Placement[], selected: string | null): Placement[] {
  return [...list].sort((a, b) => (a.name === selected ? 1 : 0) - (b.name === selected ? 1 : 0) || b.w * b.h - a.w * a.h)
}

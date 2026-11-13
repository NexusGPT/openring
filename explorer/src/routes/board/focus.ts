// Where a placed part is in the board picture. The board pictures start at the outline's top-left corner,
// so a part at (x, y) in the record's frame sits at (x - left, y - top) in the picture. The jump is only
// offered when the picture's size matches the outline's; otherwise it is left out rather than guessed.
import type { BoardFiles } from '../../contract'
import type { Rect } from '../../components/SvgViewer'
import type { Placement } from './model'

export function findBoxFocus(board: BoardFiles | null, p: Placement | null, vb: readonly [number, number, number, number] | null): (Rect & { id: string }) | null {
  const o = board?.outline
  if (!o || !p || !vb || Math.abs(vb[2] - o.w) > 1 || Math.abs(vb[3] - o.h) > 1) return null
  const w = Math.max(p.w, 3)
  const h = Math.max(p.h, 3)
  return { x: p.x - (o.x - o.w / 2) - w / 2, y: p.y - (o.y - o.h / 2) - h / 2, w, h, id: p.name }
}

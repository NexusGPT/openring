// The board picker: one button per board (the ring board, band circuit 1 and 2, the two case boards); a band circuit
// then offers its ring sizes. Names and sizes are bundle values.
import { testId } from '../../contract'
import type { BoardGroup } from './model'

interface Props {
  groups: readonly BoardGroup[]
  group: BoardGroup
  /** the size label of the shown entry, for a group with sizes */
  size: string | null
  onGroup: (id: string) => void
  onSize: (label: string) => void
}

export function BoardPicker({ groups, group, size, onGroup, onSize }: Props) {
  const sizes = group.entries.flatMap((e) => (e.size_label ? [e.size_label] : []))
  return (
    <div className="bd-picker" data-testid={testId('board', 'picker')}>
      <div className="bd-toggle bd-boards" role="group" aria-label="Board">
        {groups.map((g) => (
          <button key={g.id} type="button" aria-pressed={g.id === group.id} onClick={() => onGroup(g.id)} data-testid={testId('board', 'pick-board')} data-board={g.id}>
            {g.title}
          </button>
        ))}
      </div>
      {sizes.length > 1 && (
        <div className="bd-row bd-sizes">
          <span className="label">Ring size</span>
          <div className="bd-toggle" role="group" aria-label="Ring size">
            {sizes.map((s) => (
              <button key={s} type="button" aria-pressed={s === size} onClick={() => onSize(s)} data-testid={testId('board', 'pick-size')} data-size={s}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

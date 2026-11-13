// Copper layers one at a time, all stacked, or none (the outline and the parts only). Layer names are the board data's words.
import { testId } from '../../contract'
import type { BoardEntry, LayerChoice } from './model'

interface Props {
  entry: BoardEntry
  choice: LayerChoice
  onChange: (c: LayerChoice) => void
}

export function LayerToggle({ entry, choice, onChange }: Props) {
  if (entry.layers.length === 0) return null
  return (
    <div className="bd-toggle" role="group" aria-label="Copper layer" data-testid={testId('board', 'layers')}>
      {entry.layers.map((l) => (
        <button
          key={l.id} type="button" aria-pressed={choice === l.id} disabled={!l.svg} title={l.svg ? `${l.items} copper items` : 'No picture for this layer'}
          onClick={() => onChange(l.id)} data-testid={testId('board', 'layer')} data-layer={l.id}
        >
          {l.label}
        </button>
      ))}
      {entry.layers.length > 1 && (
        <button type="button" aria-pressed={choice === 'all'} onClick={() => onChange('all')} data-testid={testId('board', 'layer-all')}>All layers</button>
      )}
      <button type="button" aria-pressed={choice === 'none'} onClick={() => onChange('none')} data-testid={testId('board', 'layer-none')}>No copper</button>
    </div>
  )
}

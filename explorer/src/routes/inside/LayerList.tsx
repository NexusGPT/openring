import { testId } from '../../contract'
import type { LayerRow, ObjectRow } from './model'

/** The layers of the ring with their part count. A click isolates one on the stage and lists its parts;
 *  a second click (or "All layers") shows the whole ring again. */
export function LayerList({ rows, total, isolated, onIsolate, objects, selectedId, onPick }: {
  rows: LayerRow[]
  total: number
  isolated: string | null
  onIsolate(id: string | null): void
  objects: ObjectRow[]
  selectedId: string | null
  onPick(o: ObjectRow): void
}) {
  return (
    <section className="sec in-layers" aria-labelledby="inside-layers" data-testid={testId('inside', 'layers')}>
      <div className="sec-row">
        <h2 className="label sec-title" id="inside-layers">{rows.length ? `Layers of the ring · ${rows.length} layers · ${total} parts` : 'Layers of the ring'}</h2>
        {isolated && (
          <button type="button" className="in-all" data-testid={testId('inside', 'layers-all')} onClick={() => onIsolate(null)}>
            All layers
          </button>
        )}
      </div>
      {rows.length === 0 && <p className="muted in-nothing">No layers to show yet.</p>}
      <ul>
        {rows.map((r) => (
          <li key={r.id}>
            <button
              type="button"
              className="in-layer"
              data-testid={testId('inside', 'layer-row')}
              data-layer={r.id}
              aria-pressed={isolated === r.id}
              onClick={() => onIsolate(isolated === r.id ? null : r.id)}
            >
              <span>{r.label}</span>
              <span className="muted">{r.count === 1 ? '1 part' : `${r.count} parts`}</span>
            </button>
            {isolated === r.id && (
              <ul className="in-objects" data-testid={testId('inside', 'layer-parts')}>
                {objects.map((o) => (
                  <li key={o.name}>
                    <button
                      type="button"
                      data-testid={testId('inside', 'layer-part')}
                      data-object={o.name}
                      data-part-id={o.partId ?? undefined}
                      aria-pressed={o.partId !== null && o.partId === selectedId}
                      onClick={() => onPick(o)}
                    >
                      <span>{o.label}</span>
                      {o.ref && <span className="label">{o.ref}</span>}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}

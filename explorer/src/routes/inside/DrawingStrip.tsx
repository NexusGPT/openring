import { useRef } from 'react'
import { fileUrl } from '../../data'
import { testId } from '../../contract'
import { VIEW_NAMES, viewFor, fileFor, sheetFor, type MakerSet, type ViewName } from './makerFiles'

export interface StripData {
  name: string
  /** the main sizes as the parts-list line gives them, or null */
  sizes: string | null
  set: MakerSet
  ringSize: number | null
}

const VIEW_WORD: Record<ViewName, string> = { front: 'Front', side: 'Side', top: 'Top' }

/** The strip under the ring: the part's flat views with its main sizes, a ring-size switch (only for a part
 *  that has files per ring size) and the full drawing. A view that is not drawn yet says so. It slides up when
 *  `open` and keeps its last content while it slides down. */
export function DrawingStrip({ open, data, onSize }: { open: boolean; data: StripData | null; onSize(n: number): void }) {
  const last = useRef<StripData | null>(data)
  if (open && data) last.current = data
  const d = last.current
  if (!d) return <section className="in-strip" data-open="false" aria-hidden="true" data-testid={testId('inside', 'drawing-strip')} />
  const drawing = fileFor(d.set, 'drawing', d.ringSize)
  const sheet = sheetFor(d.set, d.ringSize)
  const missing = sheet ? [] : VIEW_NAMES.filter((v) => !viewFor(d.set, v, d.ringSize))
  return (
    <section className="in-strip" data-open={open} aria-hidden={!open} aria-label="Drawing" data-testid={testId('inside', 'drawing-strip')}>
      <header className="in-strip-head">
        <div className="in-strip-title">
          <span className="label">Drawing</span>
          <span className="in-strip-name">{d.name}</span>
        </div>
        {d.set.sizes.length > 1 && (
          <div className="in-sizes" role="group" aria-label="Ring size" data-testid={testId('inside', 'size-switch')}>
            <span className="label">Ring size</span>
            {d.set.sizes.map((n) => (
              <button key={n} type="button" aria-pressed={n === d.ringSize} data-size={n} tabIndex={open ? 0 : -1} onClick={() => onSize(n)}>{n}</button>
            ))}
          </div>
        )}
        {drawing ? (
          <a className="in-full" href={fileUrl(drawing.path)} target="_blank" rel="noopener noreferrer" tabIndex={open ? 0 : -1} data-testid={testId('inside', 'full-drawing')}>Full drawing ↗</a>
        ) : (
          <span className="in-full in-off" aria-disabled="true" data-testid={testId('inside', 'full-drawing')}>Full drawing: not on disk</span>
        )}
      </header>
      {sheet ? (
        <figure className="in-sheet" data-testid={testId('inside', 'drawing-sheet')}>
          <img src={fileUrl(sheet.path)} alt={`Drawing of ${d.name}: front, side and top views`} />
        </figure>
      ) : (
      <div className="in-views">
        {VIEW_NAMES.map((v) => {
          const f = viewFor(d.set, v, d.ringSize)
          return (
            <figure key={v} className="in-view" data-view={v} data-drawn={f ? 'yes' : 'no'} data-testid={testId('inside', 'drawing-view')}>
              <div className="in-view-box">
                {f ? <img src={fileUrl(f.path)} alt={`${VIEW_WORD[v]} view of ${d.name}`} /> : <span className="in-view-none">Not drawn yet</span>}
              </div>
              <figcaption className="label">{VIEW_WORD[v]}</figcaption>
            </figure>
          )
        })}
      </div>
      )}
      <p className="in-strip-foot" data-testid={testId('inside', 'strip-sizes')}>
        {d.sizes ? <><span className="label">Main sizes</span> {d.sizes} mm</> : <span className="muted">No main sizes in the parts list yet.</span>}
        {missing.length > 0 && <span className="muted" data-testid={testId('inside', 'strip-missing')}>{` Not drawn yet: ${missing.join(', ')}.`}</span>}
      </p>
    </section>
  )
}

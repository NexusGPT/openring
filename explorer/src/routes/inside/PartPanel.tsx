// The right panel for a chosen part. A made-to-drawing part: name, "Made to drawing", plain words, then
// under a rule "For the maker" (specification, four files, links out). A bought part keeps the part card and
// adds its maker, order code and datasheet. Every file button is a link when the file is listed, else greyed.
import { Link } from '../../app/router'
import { PartCard, sourceLinks } from '../../components/PartCard'
import { FILES_TO } from '../../app/route-names'
import { WORDS, testId, type AreaState, type Files, type PartNotes, type PartsLine } from '../../contract'
import { fileUrl } from '../../data'
import { FILE_KINDS, FILE_LABEL, fileFor, type MakerSet } from './makerFiles'

type Note = PartNotes['notes'][string] | null | undefined
type Legend = Parameters<typeof PartCard>[0]['legend']

/** Source, Parts line, Maker files: the three ways out of the card. */
function LinksOut({ id, line, files }: { id: string; line: PartsLine; files: Files | null }) {
  const src = sourceLinks(line, files).find((l) => l.href)
  return (
    <ul className="in-out" data-testid={testId('inside', 'links-out')}>
      <li>{src?.href ? <a href={src.href} target="_blank" rel="noopener noreferrer" data-testid={testId('inside', 'link-source')}>Source ↗</a> : <span className="in-off" aria-disabled="true">Source: {WORDS.notOnDisk}</span>}</li>
      <li><Link to={`/parts?part=${encodeURIComponent(id)}`} data-testid={testId('inside', 'link-parts-line')}>Parts line →</Link></li>
      <li><Link to={FILES_TO} data-testid={testId('inside', 'link-maker-files')}>Maker files →</Link></li>
    </ul>
  )
}

function Spec({ line }: { line: PartsLine }) {
  const rows: [string, string | null][] = [
    ['Size', line.size_mm ? `${line.size_mm} mm` : null],
    ['How many', line.quantity > 0 ? `${line.quantity} in the ring` : null],
    ['What it does', line.function],
    ['Key figure', line.key_figures],
    ['Still to settle', line.open_action],
  ]
  return (
    <dl className="in-spec" data-testid={testId('inside', 'spec')}>
      {rows.filter((r): r is [string, string] => r[1] !== null && r[1] !== '').map(([k, v]) => (
        <div key={k}><dt className="label">{k}</dt><dd>{v}</dd></div>
      ))}
    </dl>
  )
}

export function MadePanel({ id, line, note, files, set, ringSize }: {
  id: string
  line: PartsLine
  note: Note
  files: Files | null
  set: MakerSet
  ringSize: number | null
}) {
  return (
    <article className="in-made" data-testid={testId('inside', 'part-card')} data-part-id={id} data-made="true">
      <div className="label">Made to drawing</div>
      <h3 className="display in-made-h">{line.item}</h3>
      {note?.what && <p className="in-plain">{note.what}</p>}
      {note?.why && <p className="in-plain">{note.why}</p>}
      <div className="in-rule"><span className="label">For the maker</span></div>
      <Spec line={line} />
      <div className="in-files" data-testid={testId('inside', 'maker-files')}>
        {FILE_KINDS.map((k) => {
          const f = fileFor(set, k, ringSize)
          return f ? (
            <a key={k} className="in-file" href={fileUrl(f.path)} download data-file={k} data-testid={testId('inside', 'file-button')}>{FILE_LABEL[k]}</a>
          ) : (
            <span key={k} className="in-file in-off" aria-disabled="true" data-file={k} data-testid={testId('inside', 'file-button')}>
              {FILE_LABEL[k]}<em>{WORDS.notOnDisk}</em>
            </span>
          )
        })}
      </div>
      <LinksOut id={id} line={line} files={files} />
    </article>
  )
}

/** A part that is bought: the part card, then maker, order code and datasheet in one block, then the links out. */
export function BoughtPanel({ id, line, note, legend, files, areaState }: {
  id: string
  line: PartsLine
  note: Note
  legend: Legend
  files: Files | null
  areaState: AreaState | null
}) {
  const sheet = sourceLinks(line, files).find((l) => l.href && /\.pdf(\b|$)/i.test(l.href))
  return (
    <>
      <PartCard route="inside" partId={id} line={line} note={note ?? null} legend={legend} files={files} areaState={areaState} />
      <dl className="in-spec in-bought" data-testid={testId('inside', 'bought')}>
        <div><dt className="label">Maker</dt><dd>{line.maker ?? 'No maker named yet'}</dd></div>
        <div><dt className="label">Order code</dt><dd>{line.maker_part_number ?? 'No order code yet'}</dd></div>
        <div><dt className="label">Datasheet</dt><dd>{sheet?.href ? <a href={sheet.href} target="_blank" rel="noopener noreferrer">Open ↗</a> : <span className="muted">{WORDS.notOnDisk}</span>}</dd></div>
      </dl>
      <LinksOut id={id} line={line} files={files} />
    </>
  )
}

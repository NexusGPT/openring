// One connection in words: its two ends, what it carries, how it is made, the rows from the band and case notes,
// whether a design file draws it, and the files that prove it (with the download link the Files screen uses).
import { PartCard } from '../../components/PartCard'
import { Link } from '../../app/router'
import { fileUrl } from '../../data'
import { testId, type AreaState, type Files, type Parts } from '../../contract'
import { ConductorList } from './ConductorList'
import { isListed, lineOfId, refOf, type Notes } from './model'
import { conductorWords, isOpen, nodeOf, openWords, titleOf, type Connection, type ConnectionMap } from '../../components/wiring/wiringModel'

interface Props {
  map: ConnectionMap
  conn: Connection
  /** the part card open under the ends, if any */
  part: string | null
  parts: Parts | null
  notes: Notes | null
  files: Files | null
  areaState: AreaState | null
  /** does the board list hold this board group? (the link opens the Board screen on it) */
  hasBoard: (group: string) => boolean
  onPart: (id: string | null) => void
}

function Source({ file, files, line }: { file: string; files: Files | null; line?: string }) {
  return (
    <>
      {isListed(files, file) ? <a href={fileUrl(file)} target="_blank" rel="noreferrer">{file}</a> : <span>{file}</span>}
      {line ? `, ${line}` : ''}
    </>
  )
}

export function ConnectionDetail({ map, conn, part, parts, notes, files, areaState, hasBoard, onPart }: Props) {
  const open = isOpen(conn)
  return (
    <article className="el-conn" aria-label={`Connection ${conn.id}`} data-testid={testId('electronics', 'conn-detail')} data-conn={conn.id}>
      <header className="el-conn-head">
        <p className="label">{`Connection ${conn.id}`}</p>
        <h3 className="display">{titleOf(map, conn)}</h3>
        <p className="el-conn-state" data-open={open || undefined} data-testid={testId('electronics', 'conn-state')}>
          {open ? openWords(conn) : 'Drawn in the design files.'}
          {conductorWords(conn) ? <span data-testid={testId('electronics', 'conn-conductors')}>{` ${conductorWords(conn)}.`}</span> : null}
        </p>
      </header>

      <div className="el-conn-ends">
        {conn.ends.map((e, i) => {
          const n = nodeOf(map, e.node)
          return (
            <section key={i} className="el-conn-end" aria-label={i === 0 ? 'First end' : 'Second end'} data-testid={testId('electronics', 'conn-end')} data-node={e.node}>
              <p className="label">{i === 0 ? 'From' : 'To'}</p>
              <p className="el-conn-end-name">{n?.label ?? e.node}{n?.kind === 'part' && n.scope ? <span className="muted">{` · ${n.scope}`}</span> : null}</p>
              <p className="muted">{e.text}</p>
              {n?.kind === 'board' && n.board && hasBoard(n.board) ? (
                <Link className="el-conn-link" to={`/board?board=${encodeURIComponent(n.board)}`} data-testid={testId('electronics', 'conn-open-board')}>Open this board</Link>
              ) : null}
              {n?.kind === 'part' && n.part_ids.length > 0 ? (
                <div className="el-conn-parts">
                  {n.part_ids.map((id) => (
                    <button key={id} type="button" aria-pressed={part === id} onClick={() => onPart(part === id ? null : id)} data-testid={testId('electronics', 'conn-part')} data-part={id}>
                      {refOf(id)}
                    </button>
                  ))}
                </div>
              ) : null}
            </section>
          )
        })}
      </div>

      {part && (
        <div className="el-card">
          <PartCard
            route="electronics" partId={part} line={lineOfId(parts, part)} note={notes?.[part] ?? null}
            legend={parts?.evidence_legend ?? null} files={files} areaState={areaState}
          />
        </div>
      )}

      <dl className="el-facts el-conn-facts">
        <div><dt>Carries</dt><dd>{conn.signal || 'not stated'}</dd></div>
        <div><dt>Made by</dt><dd>{conn.how.kind === 'other' ? conn.how.text : `${conn.how.kind}: ${conn.how.text}`}</dd></div>
        <div><dt>Conductors</dt><dd>{conn.how.conductors || 'not stated'}</dd></div>
        {conn.details.map((d) => (
          <div key={d.label}>
            <dt>{d.label}</dt>
            <dd>
              {d.value}
              <span className="el-src label">{' · '}<Source file={d.source.file} files={files} line={d.source.line ? `line ${d.source.line}` : undefined} /></span>
            </dd>
          </div>
        ))}
        <div><dt>In the design files</dt><dd>{conn.drawn.words}</dd></div>
      </dl>

      <ConductorList conn={conn} file={map.conductor_file} files={files} />

      <section className="el-conn-proof" aria-label="Files that prove it" data-testid={testId('electronics', 'conn-proof')}>
        <h4 className="label">Files that prove it</h4>
        <ul>
          <li><Source file={conn.source.file} files={files} line={conn.source.line ? `line ${conn.source.line}` : undefined} /></li>
          {conn.proof.map((p) => (
            <li key={p.file}>
              <Source file={p.file} files={files} line={`${p.lines.length > 1 ? 'lines' : 'line'} ${p.lines.join(', ')}${p.section ? `, section "${p.section}"` : ''}`} />
            </li>
          ))}
        </ul>
      </section>
    </article>
  )
}

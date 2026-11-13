// The conductors of one connection, one row each, read from the conductor lines of the data: signal, first terminal, last terminal,
// carrier and state. A row opens to show the join at each end, the length for the chosen ring size and the source line.
import { useState } from 'react'
import { testId, type Files } from '../../contract'
import { fileUrl } from '../../data'
import { isListed } from './model'
import { conductorProblem, lengthsFor, signalWords, sizesOf, terminalWords, type Conductor, type ConductorFile, type Connection } from '../../components/wiring/wiringModel'

interface Props {
  conn: Connection
  file: ConductorFile | undefined
  files: Files | null
}

function SourceLine({ file, line, files }: { file: string; line: number | null; files: Files | null }) {
  return (
    <>
      {isListed(files, file) ? <a href={fileUrl(file)} target="_blank" rel="noreferrer">{file}</a> : <span>{file}</span>}
      {line ? `, line ${line}` : ''}
    </>
  )
}

function Opened({ k, size, files }: { k: Conductor; size: string | null; files: Files | null }) {
  const lens = lengthsFor(k, size)
  return (
    <div className="el-cd-open" data-testid={testId('electronics', 'conductor-open')}>
      {(['first', 'last'] as const).map((w) => (
        <p key={w}><span className="label">{w === 'first' ? 'First end' : 'Last end'}</span>{` ${k[w].board}, ${k[w].face}; joined: ${k[w].join}`}</p>
      ))}
      <p>
        <span className="label">Length</span>
        {size === null ? ' no length in the file' : lens.length === 0 ? ` no length in the file for ${size}` : ` ${lens.map((l) => `${l.kind === 'copper' ? 'copper' : 'cut'} ${l.mm} mm`).join(' · ')} for ${size}`}
      </p>
      <p><span className="label">Carrier</span>{` ${k.carrier.text}`}</p>
      {k.state_reason && <p><span className="label">State</span>{` ${k.state_reason}`}</p>}
      <p className="el-src label"><SourceLine file={k.source.file} line={k.source.line} files={files} /></p>
    </div>
  )
}

export function ConductorList({ conn, file, files }: Props) {
  const [open, setOpen] = useState<string | null>(null)
  const sizes = sizesOf(conn)
  const [chosen, setChosen] = useState<string | null>(null)
  const size = chosen && sizes.includes(chosen) ? chosen : (sizes[0] ?? null)
  const problem = conductorProblem(conn, file)
  const lines = file?.status === 'ok' ? (conn.conductor_lines ?? []) : []
  return (
    <section className="el-cd" aria-label="Conductors" data-testid={testId('electronics', 'conductors')}>
      <h4 className="label">Conductors</h4>
      {problem && <p className="el-none el-conn-note" role="status" data-testid={testId('electronics', 'conductor-state')}>{problem}</p>}
      {sizes.length > 0 && lines.length > 0 && (
        <div className="el-cd-sizes" role="group" aria-label="Ring size for the lengths">
          <span className="label">Ring size</span>
          {sizes.map((s) => (
            <button key={s} type="button" aria-pressed={s === size} onClick={() => setChosen(s)} data-testid={testId('electronics', 'conductor-size')} data-size={s}>{s}</button>
          ))}
        </div>
      )}
      {lines.length > 0 && (
        <ul className="el-cd-list">
          {lines.map((k) => (
            <li key={k.id} data-testid={testId('electronics', 'conductor-row')} data-conductor={k.id} data-open={open === k.id || undefined}>
              <button type="button" aria-expanded={open === k.id} onClick={() => setOpen(open === k.id ? null : k.id)}>
                <span className="el-cd-id">{k.id}</span>
                <span className="el-cd-sig">{signalWords(k)}</span>
                <span className="el-cd-end">{terminalWords(k.first)}</span>
                <span className="el-cd-end">{terminalWords(k.last)}</span>
                <span className="el-cd-carrier">{k.carrier.kind}</span>
                <span className="el-cd-state">{k.state}</span>
              </button>
              {open === k.id && <Opened k={k} size={size} files={files} />}
            </li>
          ))}
        </ul>
      )}
      {file?.status === 'ok' && (conn.no_conductor ?? []).length > 0 && (
        <div className="el-cd-none" data-testid={testId('electronics', 'conductor-none')}>
          <p className="label">No conductor</p>
          {(conn.no_conductor ?? []).map((n) => (
            <p key={n.id}>{`${n.id}: ${n.reason}`}<span className="el-src label">{' · '}<SourceLine file={n.source.file} line={n.source.line} files={files} /></span></p>
          ))}
        </div>
      )}
    </section>
  )
}

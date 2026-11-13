// The same connections as a table: id, the two ends, what it carries, how it is made, and whether a file draws it.
import { useState } from 'react'
import { testId } from '../../contract'
import { isOpen, matchesConnection, nodeLabel, type ConnectionMap } from '../../components/wiring/wiringModel'

interface Props {
  map: ConnectionMap
  selected: string | null
  onSelect: (id: string) => void
}

export function ConnectionList({ map, selected, onSelect }: Props) {
  const [q, setQ] = useState('')
  const rows = map.connections.filter((c) => matchesConnection(map, c, q))
  return (
    <section className="el-table el-conn-list" aria-label="Connections as a list" data-testid={testId('electronics', 'conn-list')}>
      <div className="el-find">
        <input
          type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Find a connection by part, signal or carrier"
          aria-label="Find a connection" data-testid={testId('electronics', 'conn-find')}
        />
        <span className="label" aria-live="polite">{`${rows.length} of ${map.connections.length}`}</span>
      </div>
      <table>
        <thead>
          <tr>
            {['Id', 'From', 'To', 'Carries', 'Made by', 'In the design files'].map((c) => <th key={c} scope="col" className="label">{c}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.id} data-selected={selected === c.id || undefined} data-testid={testId('electronics', 'conn-row')} data-conn={c.id}>
              <td data-col="first">
                <button type="button" aria-pressed={selected === c.id} onClick={() => onSelect(c.id)} data-testid={testId('electronics', 'conn-row-button')} data-conn={c.id}>{c.id}</button>
              </td>
              <td>{nodeLabel(map, c.ends[0].node)}</td>
              <td>{nodeLabel(map, c.ends[1].node)}</td>
              <td className="el-conn-signal">{c.signal}</td>
              <td>{c.how.kind === 'other' ? c.how.text : c.how.kind}</td>
              <td data-open={isOpen(c) || undefined}>{isOpen(c) ? (c.drawn.state === 'text-only' ? 'text only' : 'not drawn') : 'drawn'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <p className="el-none muted">No connection matches.</p>}
    </section>
  )
}

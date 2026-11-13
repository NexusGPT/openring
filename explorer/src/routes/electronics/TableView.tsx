// A table copied from a design document: pin plan or power budget. The cells are text; the source shows below.
import { useState } from 'react'
import { fileUrl } from '../../data'
import { testId, type Electronics, type Files } from '../../contract'
import { filterRows, isListed } from './model'

type Table = Electronics['pin_plan']

interface Props {
  name: 'pin-plan' | 'power-budget'
  title: string
  table: Table
  files: Files | null
  /** show the find box (long tables) */
  searchable?: boolean
}

export function TableView({ name, title, table, files, searchable }: Props) {
  const [q, setQ] = useState('')
  const rows = searchable ? filterRows(table.rows, q) : table.rows
  const src = table.source.file
  return (
    <section className="el-table" data-testid={testId('electronics', name)} aria-label={title}>
      {searchable && (
        <div className="el-find">
          <input
            type="search" value={q} onChange={(e) => setQ(e.target.value)}
            placeholder={`Find in ${title.toLowerCase()}`} aria-label={`Find in ${title.toLowerCase()}`}
            data-testid={testId('electronics', 'table-find')}
          />
          <span className="label" aria-live="polite">{`${rows.length} of ${table.rows.length}`}</span>
        </div>
      )}
      <table>
        <thead>
          <tr>{table.columns.map((c) => <th key={c} scope="col" className="label">{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} data-testid={testId('electronics', name === 'pin-plan' ? 'pin-row' : 'power-row')}>
              {table.columns.map((c, j) => <td key={c} data-col={j === 0 ? 'first' : undefined}>{r[j] ?? ''}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <p className="el-none muted">Nothing matches.</p>}
      <p className="el-src label">
        {'Copied from '}
        {isListed(files, src) ? <a href={fileUrl(src)} target="_blank" rel="noreferrer">{src}</a> : <span>{src}</span>}
        {`, line ${table.source.line}`}
      </p>
    </section>
  )
}

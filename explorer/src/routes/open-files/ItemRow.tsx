// One open item. The left column says who must act or when it was said; the right column says what.
import { testId } from '../../contract'
import { fileUrl, type RecordState } from '../../data'
import type { Files } from '../../contract'
import { formatDay } from './format'
import type { Row, Source } from './model'

function SourceLink({ source, files }: { source: Source; files: RecordState<Files> | null }) {
  const listed = !!files?.data?.files.some((f) => f.path === source.file)
  const text = source.line ? `${source.file}, line ${source.line}` : source.file
  return listed ? (
    <a className="item-src" href={fileUrl(source.file)} target="_blank" rel="noopener noreferrer" data-testid={testId('open', 'item-source')}>
      {text}
    </a>
  ) : (
    <span className="item-src" data-testid={testId('open', 'item-source')}>{text}</span>
  )
}

export function ItemRow({ row, files }: { row: Row; files: RecordState<Files> | null }) {
  const src = <SourceLink source={row.source} files={files} />
  const base = { 'data-testid': testId('open', 'item-row'), 'data-id': row.id, 'data-group': row.group } as const
  if (row.group === 'supplier') {
    return (
      <li className="item" {...base}>
        <span className="item-lead" data-field="who" data-testid={testId('open', 'item-who')}>{row.who}</span>
        <div className="item-main">
          {row.title !== row.ask ? <p className="item-title">{row.title}</p> : null}
          <p className="item-text" data-testid={testId('open', 'item-ask')}>{row.ask}</p>
          {src}
        </div>
      </li>
    )
  }
  if (row.group === 'decision') {
    return (
      <li className="item" {...base} data-date={row.date}>
        <span className="item-lead"><time dateTime={row.date}>{formatDay(row.date)}</time></span>
        <div className="item-main">
          <p className="item-quote">{row.quote}</p>
          <p className="item-by">{row.speaker}</p>
          {src}
        </div>
      </li>
    )
  }
  return (
    <li className="item" {...base}>
      <span className="item-lead label">{row.id}</span>
      <div className="item-main">
        <p className="item-title">{row.group === 'bench' ? row.title : row.text}</p>
        {row.group === 'bench' && row.detail ? <p className="item-text">{row.detail}</p> : null}
        {src}
      </div>
    </li>
  )
}

import { testId, type Files, type KeyNumbers as KeyNumbersRecord } from '../../contract'
import { fileUrl, type RecordState } from '../../data'
import { HOME_WORDS, capitalise, factText, leftOut } from './model'

function Source({ file, line: ln, listed }: { file: string; line: number | null; listed: boolean }) {
  const line = ln === null ? '' : `, line ${ln}`
  return (
    <span className="kn-source">
      <span className="label">{HOME_WORDS.source}</span>{' '}
      {listed ? (
        <a href={fileUrl(file)} target="_blank" rel="noreferrer" data-testid={testId('home', 'key-source')}>
          {file}{line}
        </a>
      ) : (
        <span>
          {file}{line} ({HOME_WORDS.notListed})
        </span>
      )}
    </span>
  )
}

/** The key numbers: label and value first; where each comes from appears on hover or focus. */
export function KeyNumbers({ rec, files, message }: { rec: RecordState<KeyNumbersRecord>; files: RecordState<Files> | null; message: string | null }) {
  const listed = new Set(files?.data?.files.map((f) => f.path) ?? [])
  const omitted = leftOut(message)
  const dimmed = rec.status === 'stale'
  return (
    <ul className="kn" data-dimmed={dimmed ? 'true' : undefined}>
      {rec.data?.facts.map((f) => (
        <li key={f.id} className="kn-row" data-testid={testId('home', 'key-number')} data-fact={f.id} tabIndex={0}>
          <span className="kn-label">{f.label}</span>
          <span className="kn-value">{factText(f)}</span>
          <Source file={f.source.file} line={f.source.line} listed={listed.has(f.source.file)} />
        </li>
      ))}
      {omitted.map((o) => (
        <li key={o.name} className="kn-row" data-testid={testId('home', 'key-number')} data-fact={o.name} data-left-out="true" tabIndex={0}>
          <span className="kn-label">{capitalise(o.name)}</span>
          <span className="kn-value kn-unknown">{HOME_WORDS.notKnown}</span>
          <span className="kn-source">{o.reason}</span>
        </li>
      ))}
    </ul>
  )
}

// The state of one board, in the words the data holds: 'routed and checked: ...' or 'not finished: N connections open, M violations',
// with the date and time of the board file and of the rules check. A board whose check did not run says why.
import { fileUrl } from '../../data'
import { testId, type Files } from '../../contract'
import { stampWords, type BoardEntry } from './model'

export function StateLine({ entry, files }: { entry: BoardEntry; files: Files | null }) {
  const st = entry.state
  const listed = !!entry.file && !!files?.files.some((f) => f.path === entry.file)
  return (
    <div className="bd-state" role="status" data-status={st.status} data-testid={testId('board', 'state')}>
      <p className="bd-state-words" data-testid={testId('board', 'state-words')}>{st.words}</p>
      <p className="label bd-state-stamp">
        {entry.file ? (
          <>
            {'Board file '}
            {listed ? <a href={fileUrl(entry.file)} target="_blank" rel="noreferrer">{entry.file.split('/').pop()}</a> : <span>{entry.file.split('/').pop()}</span>}
            {entry.file_time ? ` of ${stampWords(entry.file_time)}` : ''}
          </>
        ) : 'No board file'}
        {st.checked_at ? ` · rules check of ${stampWords(st.checked_at)}` : ''}
      </p>
      {entry.notes.map((n) => <p key={n} className="bd-state-note muted">{n}</p>)}
      {entry.missing.length > 0 && <p className="bd-state-note muted">{`Missing: ${entry.missing.join('; ')}.`}</p>}
    </div>
  )
}

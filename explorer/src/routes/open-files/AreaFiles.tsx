// Every file, one group per area. Groups are closed until the owner opens one; the word box narrows all
// groups at once and opens the ones it found rows in.
import { useMemo, useState } from 'react'
import { testId } from '../../contract'
import { Disclosure } from './Disclosure'
import { FileLine } from './FileLine'
import { areaGroups, matching, type FileRow } from './filesModel'
import { formatSize } from './format'

export function AreaFiles({ files }: { files: FileRow[] }) {
  const [q, setQ] = useState('')
  const groups = useMemo(() => areaGroups(files), [files])
  const searching = q.trim() !== ''
  const found = searching ? groups.reduce((n, g) => n + matching(g.files, q).length, 0) : files.length
  return (
    <div className="area-files">
      <div className="find">
        <input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Find a file by name"
          aria-label="Find a file by name"
          data-testid={testId('open', 'file-search')}
        />
        <span className="label" aria-live="polite">{searching ? `${found} found` : `${files.length} files`}</span>
      </div>
      {groups.map((g) => {
        const rows = matching(g.files, q)
        return (
          <Disclosure
            key={g.area}
            head={g.label}
            meta={searching ? `${rows.length} of ${g.files.length}` : `${g.files.length} files · ${formatSize(g.bytes)}`}
            open={searching ? rows.length > 0 : null}
            testId={testId('open', 'file-group')}
            data-area={g.area}
          >
            <ul className="fl-list">{(searching ? rows : g.files).map((f) => <FileLine key={f.path} file={f} />)}</ul>
          </Disclosure>
        )
      })}
      {searching && found === 0 ? <p className="quiet">No file has that word in its name.</p> : null}
    </div>
  )
}

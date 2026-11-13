// One file: its name, size and date, and the two things the owner does with it, open (new tab) or save.
import { testId } from '../../contract'
import { fileUrl } from '../../data'
import { baseName, dirName, formatDay, formatSize } from './format'
import type { FileRow } from './filesModel'

export function FileLine({ file, scope = 'file-row', title }: { file: FileRow; scope?: 'file-row' | 'set-row'; title?: string }) {
  const name = baseName(file.path)
  const dir = dirName(file.path)
  const url = fileUrl(file.path)
  return (
    <li className="fl" data-testid={testId('open', scope)} data-path={file.path}>
      <span className="fl-name">
        <span className="fl-base" title={file.path}>{title ?? name}</span>
        {title || dir ? <span className="fl-dir">{title ? name : dir}</span> : null}
      </span>
      <span className="fl-meta">
        <span data-testid={testId('open', 'file-size')}>{formatSize(file.size_bytes)}</span>
        <span data-testid={testId('open', 'file-date')}>{formatDay(file.modified)}</span>
      </span>
      <span className="fl-acts">
        <a href={url} target="_blank" rel="noopener noreferrer" data-testid={testId('open', 'file-open')} aria-label={`Open ${name} in a new tab`}>Open</a>
        <a href={url} download={name} data-testid={testId('open', 'file-download')} aria-label={`Download ${name}`}>Save</a>
      </span>
    </li>
  )
}

import { testId, type Case, type Files } from '../../contract'
import { fileUrl } from '../../data'
import { factText } from './model'

/** The case's numbers: label left, value right; where each comes from appears on hover or focus. */
export function Facts({ facts, files }: { facts: Case['facts']; files: Files | null }) {
  const listed = new Set(files?.files.map((f) => f.path) ?? [])
  return (
    <ul className="cs-facts">
      {facts.map((f) => {
        const where = `${f.source.file}${f.source.line === null ? '' : `, line ${f.source.line}`}`
        return (
          <li key={f.id} className="cs-fact" data-testid={testId('case', 'fact')} data-fact={f.id} tabIndex={0}>
            <span className="cs-fact-label">{f.label}</span>
            <span className="cs-fact-value">{factText(f)}</span>
            <span className="cs-fact-source">
              {listed.has(f.source.file) ? (
                <a href={fileUrl(f.source.file)} target="_blank" rel="noreferrer">{where}</a>
              ) : (
                where
              )}
            </span>
          </li>
        )
      })}
    </ul>
  )
}

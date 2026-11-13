// Totals of the ring list and the export. The numbers are the bundle's own totals, never counted here.
import { testId, type Files, type Parts } from '../../contract'
import { fileUrl } from '../../data'
import { linesWord, partsWord, pricedSum } from './model'

const base = (p: string): string => p.split('/').pop() ?? p

export function Totals({ parts, files, source }: { parts: Parts; files: Files | null; source: string | null }) {
  const t = parts.totals.ring
  const sum = pricedSum(parts, 'ring')
  const listed = !!source && !!files?.files.some((f) => f.path === source)
  return (
    <div className="pt-totals-row">
      <p className="pt-totals" data-testid={testId('parts', 'totals')}>
        <strong>{linesWord(t.lines)}</strong> · <strong>{partsWord(t.parts)}</strong>
        <span className="pt-sub">
          {sum ? `Priced so far: ${sum}. ` : 'No price known yet. '}
          {t.unpriced_lines > 0 ? `${linesWord(t.unpriced_lines)} without a price.` : ''}
        </span>
      </p>
      {listed && source ? (
        <a className="pt-export" data-testid={testId('parts', 'export-csv')} href={fileUrl(source)} download={base(source)}>
          Export CSV
        </a>
      ) : (
        <span className="pt-export" aria-disabled="true" role="link" data-testid={testId('parts', 'export-csv')} title="The source list is not in the files list">
          Export CSV
        </span>
      )}
    </div>
  )
}

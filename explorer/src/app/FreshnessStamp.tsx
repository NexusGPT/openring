import { banner, testId } from '../contract'
import { useManifest } from '../data'
import { stampOf } from './freshness'

/** In the tab bar: when the data was built and from which commit. Never a fixed string or the clock. */
export function FreshnessStamp() {
  const { data: manifest, isPending } = useManifest()
  if (isPending) return <div className="stamp" data-testid={testId('app', 'freshness-stamp')} aria-hidden="true" />
  if (!manifest) {
    const b = banner({ kind: 'missing' })
    return (
      <div className="stamp" data-testid={testId('app', 'freshness-stamp')} data-dirty="false" data-kind-stamp="missing">
        {b.sentence}
      </div>
    )
  }
  const s = stampOf(manifest)
  return (
    <div className="stamp" data-testid={testId('app', 'freshness-stamp')} data-dirty={String(s.dirty)} data-built-at={manifest.built_at}>
      {s.text}
    </div>
  )
}

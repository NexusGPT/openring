// "Download partner bundle": one click, the whole file set as a zip, and the list of what is inside.
// Disabled, with the command, when the collector has not made the zip (or the file is not served).
import { useEffect, useState } from 'react'
import { testId, type Files } from '../../contract'
import { dataUrl } from '../../data'
import { Disclosure } from './Disclosure'
import { baseName, formatSize } from './format'

type Bundle = Files['bundle']

/** True when the zip answers and is not an HTML page standing in for it. */
function useServed(bundle: Bundle): boolean | null {
  const [served, setServed] = useState<boolean | null>(null)
  const file = bundle?.file ?? null
  useEffect(() => {
    if (!file) return setServed(false)
    let live = true
    fetch(dataUrl(file), { method: 'HEAD' })
      .then((r) => live && setServed(r.ok && !(r.headers.get('content-type') ?? '').includes('text/html')))
      .catch(() => live && setServed(false))
    return () => {
      live = false
    }
  }, [file])
  return file ? served : false
}

const WORDS = {
  title: 'For a build partner',
  button: 'Download partner bundle',
  what: 'The complete file set in one zip.',
  off: 'run npm run collect',
} as const

export function BundleCard({ bundle }: { bundle: Bundle }) {
  const served = useServed(bundle)
  const ready = !!bundle && served === true
  return (
    <div className="bundle" data-testid={testId('open', 'bundle')} data-ready={String(ready)}>
      <p className="label">{WORDS.title}</p>
      <p className="bundle-what">{ready ? `${WORDS.what} ${formatSize(bundle.size_bytes)}, ${bundle.contents.length} files.` : WORDS.what}</p>
      {ready ? (
        <a className="bundle-btn" href={dataUrl(bundle.file)} download={baseName(bundle.file)} data-testid={testId('open', 'download-bundle')}>
          <span>{WORDS.button}</span>
        </a>
      ) : (
        <button type="button" className="bundle-btn" disabled data-testid={testId('open', 'download-bundle')} aria-busy={served === null && !!bundle}>
          <span>{WORDS.button}</span>
          <span className="bundle-off">{served === null && bundle ? 'checking the file' : WORDS.off}</span>
        </button>
      )}
      {bundle ? (
        <Disclosure head="What is inside" meta={`${bundle.contents.length} files`} testId={testId('open', 'bundle-contents')}>
          <ul className="entries">
            {bundle.contents.map((p) => (
              <li key={p} data-testid={testId('open', 'bundle-entry')}>{p}</li>
            ))}
          </ul>
        </Disclosure>
      ) : null}
    </div>
  )
}

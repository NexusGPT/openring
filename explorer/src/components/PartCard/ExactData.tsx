import { useId, useState } from 'react'
import type { Files, PartsLine } from '../../contract'
import { sourceLinks, NOT_ON_DISK } from './model'

function Row({ k, v }: { k: string; v: string | null | undefined }) {
  if (!v) return null
  return (
    <>
      <dt>{k}</dt>
      <dd>{v}</dd>
    </>
  )
}

/** The exact data, one click below the plain words. Closed = not in the page at all. */
export function ExactData({ line, files, testid }: { line: PartsLine; files: Files | null; testid: string }) {
  const [open, setOpen] = useState(false)
  const panel = useId()
  const links = sourceLinks(line, files)
  return (
    <div className="pc-exact">
      <button type="button" className="pc-exact-btn" aria-expanded={open} aria-controls={panel} data-testid={`${testid}-exact-toggle`} onClick={() => setOpen((o) => !o)}>
        <span>Exact data</span>
        <span className="pc-chev" aria-hidden="true" />
      </button>
      {open && (
        <div id={panel} className="pc-exact-panel" data-testid={`${testid}-exact`}>
          <dl className="pc-kv">
            <Row k="Maker" v={line.maker} />
            <Row k="Part number" v={line.maker_part_number} />
            <Row k="Package" v={line.package} />
            <Row k="Value" v={line.value} />
            <Row k="Price" v={line.price?.raw} />
            <Row k="Parts-list refs" v={line.refs.join(', ')} />
          </dl>
          <div className="pc-lab">Source files</div>
          <ul className="pc-links">
            {links.map((l) => (
              <li key={l.key}>
                {l.href ? (
                  <a href={l.href} target="_blank" rel="noopener noreferrer">
                    {l.label}
                  </a>
                ) : (
                  <span role="link" aria-disabled="true" className="pc-link-off">
                    {l.label} <em>{NOT_ON_DISK}</em>
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

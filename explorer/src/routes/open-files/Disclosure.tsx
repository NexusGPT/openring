// A section that opens and closes with a fade. The content stays in the page (so a search or a test can
// count it); while closed it is inert and invisible. Height follows the grid-rows transition.
import { useId, useState, type ReactNode } from 'react'

export function Disclosure({ head, meta, children, defaultOpen = false, open: forced, testId, ...attrs }: {
  head: ReactNode
  meta?: ReactNode
  children: ReactNode
  defaultOpen?: boolean
  /** when set, it wins over the user's own toggle (a search that found rows opens its groups) */
  open?: boolean | null
  testId?: string
} & Record<`data-${string}`, string | undefined>) {
  const [own, setOwn] = useState(defaultOpen)
  const open = forced ?? own
  const body = useId()
  return (
    <div className="disc" data-open={String(open)} data-testid={testId} {...attrs}>
      <button type="button" className="disc-head" aria-expanded={open} aria-controls={body} onClick={() => setOwn(!open)}>
        <span className="disc-chev" aria-hidden="true" />
        <span className="disc-title">{head}</span>
        {meta ? <span className="disc-meta label">{meta}</span> : null}
      </button>
      <Collapse open={open} id={body}>{children}</Collapse>
    </div>
  )
}

/** The fading, height-animated body. Closed content is inert and invisible but stays in the page. */
export function Collapse({ open, id, children }: { open: boolean; id?: string; children: ReactNode }) {
  return (
    <div className="disc-body" id={id} data-open={String(open)}>
      <div className="disc-inner" inert={!open}>
        {children}
      </div>
    </div>
  )
}

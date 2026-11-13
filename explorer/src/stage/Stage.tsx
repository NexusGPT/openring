// <Stage/>: the one shared 3D view. It renders a host div, mounts the engine's canvas in it and one
// transparent cell per view over the canvas (the cells take the pointer and carry the captions).
// Mount it once, in the shell; screens change its props, never its place.
import { useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore, type CSSProperties } from 'react'
import { StateBanner } from '../contract'
import { reducedMotion } from './ease'
import { getEngine } from './engine'
import { installTestApi } from './testApi'
import type { StageHover, StageProps } from './types'

const hostStyle: CSSProperties = { position: 'relative', width: '100%', height: '100%', minHeight: 0, display: 'flex', overflow: 'hidden' }
const cellStyle: CSSProperties = { position: 'relative', flex: '1 1 0', minWidth: 0, touchAction: 'none', cursor: 'grab' }
const captionStyle: CSSProperties = { position: 'absolute', left: 12, top: 10, pointerEvents: 'none' }
const tagStyle: CSSProperties = { position: 'absolute', pointerEvents: 'none', padding: '4px 8px', background: 'var(--bg)', color: 'var(--ink)', border: '1px solid var(--hairline)', whiteSpace: 'nowrap', zIndex: 2 }
const noticeStyle: CSSProperties = { position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 24, pointerEvents: 'none', color: 'var(--muted)', fontSize: 14 }

export function Stage(props: StageProps) {
  const host = useRef<HTMLDivElement>(null)
  const cells = useRef(new Map<string, HTMLElement>())
  const engine = getEngine()
  const [hover, setHover] = useState<StageHover | null>(null)
  const lastTag = useRef<StageHover | null>(null)
  if (hover) lastTag.current = hover
  const live = useRef(props)
  live.current = props
  const status = useSyncExternalStore((cb) => engine.subscribe(cb), () => engine.status())

  useEffect(() => {
    const h = host.current
    if (!h) return
    engine.attach(h)
    engine.canvas.dataset.stageId = h.closest('[data-stage-id]')?.getAttribute('data-stage-id') ?? ''
    window.__stage = installTestApi(engine)
    return () => engine.detach(h)
  }, [engine])

  useEffect(() => {
    engine.hoverCb = (h) => {
      setHover((old) => (old && h && old.node === h.node && Math.abs(old.x - h.x) < 2 && Math.abs(old.y - h.y) < 2 ? old : h))
      live.current.onHover?.(h)
    }
    return () => {
      engine.hoverCb = null
    }
  }, [engine])

  // runs after every render: the cells exist, the props are new
  useLayoutEffect(() => {
    engine.update(props, cells.current)
  })

  const exterior = props.views.find((v) => v.role === 'exterior')?.exterior
  const failed = status.split('|').some((s) => s.endsWith(':failed'))
  const route = props.route ?? 'app'
  return (
    <div ref={host} className={props.className} style={hostStyle} data-testid={`${route}.stage`} data-exterior={exterior}>
      {props.views.map((v) => (
        <div
          key={v.id}
          ref={(el) => {
            if (el) cells.current.set(v.id, el)
            else cells.current.delete(v.id)
          }}
          style={cellStyle}
          data-view={v.id}
          data-role={v.role}
          data-slab={v.slab ? 'true' : undefined}
        >
          {v.label ? <span className="label" style={captionStyle}>{v.label}</span> : null}
        </div>
      ))}
      {lastTag.current && props.labels?.[lastTag.current.node] ? (
        <span
          className="label"
          role="tooltip"
          data-testid={`${route}.part-tag`}
          data-shown={hover ? 'true' : 'false'}
          style={{ ...tagStyle, left: lastTag.current.x + 14, top: lastTag.current.y + 14, opacity: hover ? 1 : 0, transition: reducedMotion() ? 'none' : 'opacity var(--t-med, 200ms) var(--ease, ease-out)' }}
        >
          {props.labels[lastTag.current.node]}
        </span>
      ) : null}
      {failed || props.notice ? (
        <div style={noticeStyle}>
          <StateBanner route={route} spec={props.notice ?? { kind: 'missing' }} />
        </div>
      ) : null}
    </div>
  )
}

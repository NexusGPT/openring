import { useCallback, useEffect, useImperativeHandle, useLayoutEffect, useRef, useState, type KeyboardEvent, type PointerEvent, type Ref } from 'react'
import { StateBanner } from '../../contract/ui/StateBanner'
import { testId, type TestScope } from '../../contract/ids'
import type { BannerSpec } from '../../contract/vocabulary'
import { FIT, ZOOM_STEP, clampView, fitScale, scaleText, viewForRect, wheelFactor, zoomAt, type Rect, type Size, type View } from './model'
import './SvgViewer.css'

export interface SvgViewerHandle {
  /** Show the whole picture. */
  fit(): void
  /** Zoom to a rectangle given in the picture's own coordinates. */
  focusRect(rect: Rect): void
  zoomIn(): void
  zoomOut(): void
}

export interface SvgViewerProps {
  /** Host route; ids are `<route>.svg-viewer`, `.svg-viewer-zoom-in`, `-zoom-out`, `-fit`, `-scale`, `-image`. */
  route: TestScope
  /** Bundle URL of the picture, from `dataUrl()`. null or '' = the picture is missing. */
  src: string | null | undefined
  /** What the picture shows, in words (the image's alt text and the viewer's name). */
  label: string
  /** The picture's viewBox `[x, y, w, h]`; the units of `focus` rectangles. Without it the image's own size is used. */
  viewBox?: readonly [number, number, number, number]
  /** Jump to this rectangle (picture coordinates) and outline it. A new object or a new `id` jumps again. null = none. */
  focus?: (Rect & { id?: string | number }) | null
  /** Honest-state banner shown when the picture is missing. Default: "Not built yet. Run npm run collect." */
  missing?: BannerSpec
  /** Called with the zoom (1 = fit) after every change. */
  onScaleChange?: (scale: number) => void
  ref?: Ref<SvgViewerHandle>
}

const FALLBACK_BOX: Size = { w: 800, h: 600 }
const KEY_PAN = 60

export function SvgViewer({ route, src, label, viewBox, focus, missing = { kind: 'missing' }, onScaleChange, ref }: SvgViewerProps) {
  const stage = useRef<HTMLDivElement>(null)
  const [box, setBox] = useState<Size>(FALLBACK_BOX)
  const [natural, setNatural] = useState<Size | null>(null)
  const [view, setView] = useState<View>(FIT)
  const [moving, setMoving] = useState(false) // true while a drag, wheel or pinch is live: no easing then
  const [broken, setBroken] = useState(false)
  const viewRef = useRef(view)
  viewRef.current = view

  const origin = { x: viewBox?.[0] ?? 0, y: viewBox?.[1] ?? 0 }
  const pic: Size | null = viewBox ? { w: viewBox[2], h: viewBox[3] } : natural
  const picRef = useRef(pic)
  picRef.current = pic
  const boxRef = useRef(box)
  boxRef.current = box

  useLayoutEffect(() => {
    const el = stage.current
    if (!el) return
    const read = () => setBox(el.clientWidth > 0 && el.clientHeight > 0 ? { w: el.clientWidth, h: el.clientHeight } : FALLBACK_BOX)
    read()
    if (typeof ResizeObserver === 'undefined') return
    const ro = new ResizeObserver(read)
    ro.observe(el)
    return () => ro.disconnect()
  }, [src])

  useEffect(() => { setBroken(false); setNatural(null); setView(FIT) }, [src])
  useEffect(() => { onScaleChange?.(view.z) }, [view.z, onScaleChange])

  const apply = useCallback((next: View, easy = true) => {
    const p = picRef.current
    setMoving(!easy)
    setView(p ? clampView(next, p, boxRef.current) : next)
  }, [])

  const zoomBy = useCallback((factor: number, px = 0, py = 0, easy = true) => apply(zoomAt(viewRef.current, viewRef.current.z * factor, px, py), easy), [apply])
  const focusRect = useCallback((r: Rect) => {
    const p = picRef.current
    if (p) apply(viewForRect(r, p, origin, boxRef.current))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apply, origin.x, origin.y])

  useImperativeHandle(ref, () => ({ fit: () => apply(FIT), focusRect, zoomIn: () => zoomBy(ZOOM_STEP), zoomOut: () => zoomBy(1 / ZOOM_STEP) }), [apply, focusRect, zoomBy])

  const fx = focus?.x, fy = focus?.y, fw = focus?.w, fh = focus?.h, fid = focus?.id
  useEffect(() => {
    if (fx === undefined || fy === undefined || fw === undefined || fh === undefined) return
    focusRect({ x: fx, y: fy, w: fw, h: fh })
    // box.w/h: the first measure of the stage arrives after the first render; jump again so the item is centred in the real box
  }, [fx, fy, fw, fh, fid, focusRect, pic?.w, pic?.h, box.w, box.h])

  // Wheel and trackpad pinch (ctrl + wheel). Native listener: React's is passive and cannot stop the page scrolling.
  useEffect(() => {
    const el = stage.current
    if (!el) return
    const onWheel = (e: WheelEvent) => {
      e.preventDefault()
      const r = el.getBoundingClientRect()
      zoomBy(wheelFactor(e.deltaY, e.ctrlKey), e.clientX - r.left - r.width / 2, e.clientY - r.top - r.height / 2, false)
    }
    el.addEventListener('wheel', onWheel, { passive: false })
    return () => el.removeEventListener('wheel', onWheel)
  }, [zoomBy, src, broken])

  // Pointers: one finger or the mouse pans, two fingers pinch.
  const pointers = useRef(new Map<number, { x: number; y: number }>())
  const pinch = useRef<number | null>(null)
  const onDown = (e: PointerEvent<HTMLDivElement>) => {
    e.currentTarget.setPointerCapture?.(e.pointerId)
    pointers.current.set(e.pointerId, { x: e.clientX, y: e.clientY })
    if (pointers.current.size === 2) { const [a, b] = [...pointers.current.values()]; pinch.current = Math.hypot(a!.x - b!.x, a!.y - b!.y) }
  }
  const onMove = (e: PointerEvent<HTMLDivElement>) => {
    const prev = pointers.current.get(e.pointerId)
    if (!prev) return
    const cur = { x: e.clientX, y: e.clientY }
    pointers.current.set(e.pointerId, cur)
    if (pointers.current.size === 1) {
      apply({ ...viewRef.current, tx: viewRef.current.tx + cur.x - prev.x, ty: viewRef.current.ty + cur.y - prev.y }, false)
    } else if (pointers.current.size === 2 && pinch.current) {
      const [a, b] = [...pointers.current.values()]
      const d = Math.hypot(a!.x - b!.x, a!.y - b!.y)
      const r = e.currentTarget.getBoundingClientRect()
      zoomBy(d / pinch.current, (a!.x + b!.x) / 2 - r.left - r.width / 2, (a!.y + b!.y) / 2 - r.top - r.height / 2, false)
      pinch.current = d
    }
  }
  const onUp = (e: PointerEvent<HTMLDivElement>) => {
    pointers.current.delete(e.pointerId)
    pinch.current = null
    if (pointers.current.size === 0) setMoving(false)
  }

  const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
    const pan = (dx: number, dy: number) => { e.preventDefault(); const k = e.shiftKey ? 3 : 1; apply({ ...viewRef.current, tx: viewRef.current.tx + dx * KEY_PAN * k, ty: viewRef.current.ty + dy * KEY_PAN * k }) }
    switch (e.key) {
      case '+': case '=': e.preventDefault(); zoomBy(ZOOM_STEP); break
      case '-': case '_': e.preventDefault(); zoomBy(1 / ZOOM_STEP); break
      case '0': e.preventDefault(); apply(FIT); break
      case 'ArrowLeft': pan(1, 0); break
      case 'ArrowRight': pan(-1, 0); break
      case 'ArrowUp': pan(0, 1); break
      case 'ArrowDown': pan(0, -1); break
    }
  }

  const id = (el: string) => testId(route, el)
  const absent = !src || broken
  const banner: BannerSpec = broken && src ? { kind: 'unparsed', file: src.split('/').pop() ?? src } : missing
  const f = pic ? fitScale(pic, box) : 1
  const imgStyle = pic ? { width: pic.w * f, height: pic.h * f } : undefined
  // The outline lives outside the scaled layer so its line stays 2 px at any zoom.
  const k = f * view.z
  const focusStyle = focus && pic ? {
    left: box.w / 2 + view.tx + (focus.x - origin.x - pic.w / 2) * k, top: box.h / 2 + view.ty + (focus.y - origin.y - pic.h / 2) * k,
    width: focus.w * k, height: focus.h * k,
  } : null

  return (
    <div className="svgv" data-testid={id('svg-viewer')} data-scale={view.z.toFixed(3)} data-picture={absent ? 'absent' : 'ready'}>
      <div
        ref={stage}
        className="svgv-stage"
        role="group"
        aria-label={label}
        aria-roledescription="zoomable picture"
        tabIndex={0}
        data-moving={moving}
        onKeyDown={onKey}
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
      >
        {absent ? (
          <div className="svgv-missing"><StateBanner route={route} spec={banner} /></div>
        ) : (
          <div className="svgv-layer" style={{ transform: `translate(-50%, -50%) translate(${view.tx}px, ${view.ty}px) scale(${view.z})` }}>
            <img
              data-testid={id('svg-viewer-image')}
              className="svgv-img"
              src={src}
              alt={label}
              draggable={false}
              style={imgStyle}
              onLoad={(e) => setNatural({ w: e.currentTarget.naturalWidth, h: e.currentTarget.naturalHeight })}
              onError={() => setBroken(true)}
            />
          </div>
        )}
        {!absent && focusStyle ? <span className="svgv-focus" data-testid={id('svg-viewer-focus')} style={focusStyle} /> : null}
      </div>
      <div className="svgv-bar" role="toolbar" aria-label="Zoom">
        <button type="button" data-testid={id('svg-viewer-zoom-out')} aria-label="Zoom out" disabled={absent} onClick={() => zoomBy(1 / ZOOM_STEP)}>&minus;</button>
        <output data-testid={id('svg-viewer-scale')} aria-label="Zoom level">{scaleText(view.z)}</output>
        <button type="button" data-testid={id('svg-viewer-zoom-in')} aria-label="Zoom in" disabled={absent} onClick={() => zoomBy(ZOOM_STEP)}>+</button>
        <button type="button" data-testid={id('svg-viewer-fit')} className="svgv-fit" disabled={absent} onClick={() => apply(FIT)}>Fit</button>
      </div>
    </div>
  )
}

// The picture's own header and the place of a named part in it, from one fetch of the SVG per picture.
// The viewer never reads the picture; this file does, as text, and only looks for numbers.
import { useEffect, useState, type RefObject } from 'react'
import { parseViewBox, type Rect, type SvgViewerHandle } from '../../components/SvgViewer'

const cache = new Map<string, Promise<string | null>>()
function load(url: string): Promise<string | null> {
  let p = cache.get(url)
  if (!p) {
    p = fetch(url).then((r) => (r.ok ? r.text() : null)).catch(() => null)
    cache.set(url, p)
  }
  return p
}

/** The text of an SVG picture, or null while it loads or when it cannot be read. */
export function useSvgText(url: string | null): string | null {
  const [t, setT] = useState<{ url: string; text: string | null } | null>(null)
  useEffect(() => {
    let live = true
    if (url) void load(url).then((text) => live && setT({ url, text }))
    return () => { live = false }
  }, [url])
  return t && t.url === url ? t.text : null
}

export function viewBoxOfText(text: string | null): [number, number, number, number] | null {
  const m = text?.match(/<svg[\s\S]*?viewBox="([^"]+)"/)
  return m?.[1] ? parseViewBox(m[1]) : null
}

const esc = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
/** The place of a reference's label in a KiCad schematic page: a window of `w` x `h` around its text. */
export function findRefRect(text: string | null, ref: string, w = 26, h = 18): Rect | null {
  const m = text?.match(new RegExp(`<text\\s+x="([\\d.-]+)"\\s+y="([\\d.-]+)"[^>]*>${esc(ref)}</text>`))
  if (!m) return null
  const x = Number(m[1])
  const y = Number(m[2])
  // the label sits above the part, so the window is moved down to hold the part too
  return Number.isFinite(x) && Number.isFinite(y) ? { x: x - w / 2, y: y - h / 2 + h * 0.3, w, h } : null
}

/** Fit the picture again when the box it sits in changes width by more than 40 px (the panel opening wide), once it has settled. */
export function useRefit(box: RefObject<HTMLElement | null>, viewer: RefObject<SvgViewerHandle | null>): void {
  useEffect(() => {
    const el = box.current
    if (!el || typeof ResizeObserver === 'undefined') return
    let last = el.clientWidth
    let timer = 0
    const ro = new ResizeObserver(() => {
      window.clearTimeout(timer)
      timer = window.setTimeout(() => {
        if (Math.abs(el.clientWidth - last) > 40) { last = el.clientWidth; viewer.current?.fit() }
      }, 400)
    })
    ro.observe(el)
    return () => { ro.disconnect(); window.clearTimeout(timer) }
  }, [box, viewer])
}

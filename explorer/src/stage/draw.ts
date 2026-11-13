// Drawing the views into the one canvas, and measuring their DOM regions.
import type * as THREE from 'three'
import type { StageView } from './view'

export interface Rect {
  x: number
  y: number
  w: number
  h: number
}

/** DOM regions of the views, in CSS px with y from the bottom (the WebGL convention). */
export function measure(host: HTMLElement, views: ReadonlyMap<string, StageView>): { w: number; h: number; rects: Map<string, Rect> } | null {
  const hb = host.getBoundingClientRect()
  const w = Math.round(hb.width)
  const h = Math.round(hb.height)
  if (w < 1 || h < 1) return null
  const rects = new Map<string, Rect>()
  for (const [id, v] of views) {
    const b = v.el.getBoundingClientRect()
    rects.set(id, { x: Math.round(b.left - hb.left), y: Math.round(h - (b.bottom - hb.top)), w: Math.round(b.width), h: Math.round(b.height) })
  }
  return { w, h, rects }
}

/** One frame: clear once, then each ready view inside its scissor rectangle. Returns true if any view drew. */
export function drawViews(r: THREE.WebGLRenderer, views: ReadonlyMap<string, StageView>, rects: ReadonlyMap<string, Rect>): boolean {
  r.setScissorTest(false)
  r.clear()
  let drew = false
  for (const [id, v] of views) {
    const b = rects.get(id)
    if (v.state !== 'ok' || !b || b.w < 2 || b.h < 2) continue
    r.setViewport(b.x, b.y, b.w, b.h)
    r.setScissor(b.x, b.y, b.w, b.h)
    r.setScissorTest(true)
    r.render(v.scene, v.camera)
    drew = true
  }
  return drew
}

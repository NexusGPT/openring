// Pure geometry of the picture viewer. No DOM, no React: every rule here is unit-tested.
// Picture coordinates are the SVG's own viewBox units. `z` is the zoom relative to "fit": 1.0 = fit.

export interface Rect { x: number; y: number; w: number; h: number }
export interface Size { w: number; h: number }
/** Where the picture sits: its centre is the container centre plus (tx, ty) pixels, scaled by z. */
export interface View { z: number; tx: number; ty: number }

/** One button press or key press multiplies the zoom by this; four presses make exactly 4.0. */
export const ZOOM_STEP = Math.SQRT2
export const MIN_ZOOM = 0.5
export const MAX_ZOOM = 40
/** Share of the container the fitted picture fills. */
export const FIT_FILL = 0.94
/** Share of the container a jumped-to item fills. */
export const FOCUS_FILL = 0.55
/** A zoomed-in item is never shown larger than this multiple of fit, however small the rectangle. */
export const FOCUS_MAX_ZOOM = 12

export const FIT: View = { z: 1, tx: 0, ty: 0 }
const clampZ = (z: number): number => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z))

/** Pixels per picture unit at z = 1 (the fit scale). */
export function fitScale(pic: Size, box: Size): number {
  if (pic.w <= 0 || pic.h <= 0 || box.w <= 0 || box.h <= 0) return 1
  return Math.min(box.w / pic.w, box.h / pic.h) * FIT_FILL
}

/** Keep the picture from being flung out of sight: at least `keep` px of it stay inside the box. */
export function clampView(v: View, pic: Size, box: Size, keep = 48): View {
  const f = fitScale(pic, box)
  const maxX = (pic.w * f * v.z) / 2 + box.w / 2 - keep
  const maxY = (pic.h * f * v.z) / 2 + box.h / 2 - keep
  return { z: v.z, tx: Math.max(-maxX, Math.min(maxX, v.tx)), ty: Math.max(-maxY, Math.min(maxY, v.ty)) }
}

/** Zoom to `z` (clamped) keeping the box point (px, py), measured from the box centre, still. */
export function zoomAt(v: View, z: number, px: number, py: number): View {
  const nz = clampZ(z)
  const k = nz / v.z
  return { z: nz, tx: px - (px - v.tx) * k, ty: py - (py - v.ty) * k }
}

/** The view that shows `rect` (picture units) in the middle of the box, filling FOCUS_FILL of it. */
export function viewForRect(rect: Rect, pic: Size, origin: { x: number; y: number }, box: Size): View {
  const f = fitScale(pic, box)
  const fill = Math.min((box.w * FOCUS_FILL) / (Math.max(rect.w, 1e-9) * f), (box.h * FOCUS_FILL) / (Math.max(rect.h, 1e-9) * f))
  const z = Math.min(FOCUS_MAX_ZOOM, Math.max(1, fill))
  const k = f * z
  const cx = origin.x + pic.w / 2
  const cy = origin.y + pic.h / 2
  return clampView({ z, tx: -(rect.x + rect.w / 2 - cx) * k, ty: -(rect.y + rect.h / 2 - cy) * k }, pic, box)
}

/** Wheel and pinch: a smooth factor from the wheel delta (a trackpad pinch arrives as ctrl + wheel). */
export function wheelFactor(deltaY: number, pinch: boolean): number {
  return Math.exp(-deltaY * (pinch ? 0.01 : 0.0015))
}

/** The scale as the screen shows it: 4.0 reads "400 %". */
export function scaleText(z: number): string {
  return `${Math.round(z * 100)} %`
}

/** [x, y, w, h] from a viewBox attribute text; null when it is not four numbers. */
export function parseViewBox(text: string): [number, number, number, number] | null {
  const n = text.trim().split(/[\s,]+/).map(Number)
  return n.length === 4 && n.every(Number.isFinite) && n[2]! > 0 && n[3]! > 0 ? [n[0]!, n[1]!, n[2]!, n[3]!] : null
}

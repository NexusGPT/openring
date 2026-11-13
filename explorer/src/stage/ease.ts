// One easing for every transition of the stage. Duration and curve come from the shell's motion tokens
// (src/styles/tokens.css: --t-slow, --ease-settle); without them 320 ms and a smooth ease-out.
// With prefers-reduced-motion every change is instant.
const FALLBACK = { ms: 320, curve: [0.16, 1, 0.3, 1] as const }

export function reducedMotion(): boolean {
  return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches
}

function token(name: string): string {
  return typeof document === 'undefined' ? '' : getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

export interface Motion {
  ms: number
  curve: readonly [number, number, number, number]
}

export function motionTokens(): Motion {
  const t = token('--t-slow')
  const ms = /^([\d.]+)ms$/.test(t) ? Number.parseFloat(t) : /^([\d.]+)s$/.test(t) ? Number.parseFloat(t) * 1000 : FALLBACK.ms
  const m = /cubic-bezier\(([^)]+)\)/.exec(token('--ease-settle'))
  const nums = m?.[1]?.split(',').map((x) => Number.parseFloat(x)) ?? []
  const curve = nums.length === 4 && nums.every(Number.isFinite) ? (nums as unknown as Motion['curve']) : FALLBACK.curve
  return { ms: reducedMotion() ? 0 : ms, curve }
}

/** CSS cubic-bezier(x1, y1, x2, y2) evaluated at progress t (0..1). */
export function bezier(c: Motion['curve'], t: number): number {
  const [x1, y1, x2, y2] = c
  const cx = 3 * x1
  const bx = 3 * (x2 - x1) - cx
  const ax = 1 - cx - bx
  const cy = 3 * y1
  const by = 3 * (y2 - y1) - cy
  const ay = 1 - cy - by
  let s = t
  for (let i = 0; i < 8; i++) {
    const x = ((ax * s + bx) * s + cx) * s - t
    const d = (3 * ax * s + 2 * bx) * s + cx
    if (Math.abs(x) < 1e-6 || Math.abs(d) < 1e-6) break
    s -= x / d
  }
  s = Math.min(1, Math.max(0, s))
  return ((ay * s + by) * s + cy) * s
}

/** A value that eases to its goal. Setting a new goal restarts from where the value is now, so a dragged
 *  control is followed without steps, and a value set by a click animates. */
export class Tween {
  value: number
  private from: number
  private to: number
  private t0 = 0
  private ms = 0
  private curve: Motion['curve'] = FALLBACK.curve

  constructor(value = 0) {
    this.value = this.from = this.to = value
  }

  get goal(): number {
    return this.to
  }

  /** `ms`: a duration of its own (the case lid takes 600 ms); default the token's. */
  set(to: number, now: number, ms?: number): void {
    if (to === this.to) return
    const m = motionTokens()
    if (ms !== undefined && m.ms > 0) m.ms = ms
    this.from = this.value
    this.to = to
    this.t0 = now
    this.ms = m.ms
    this.curve = m.curve
    if (m.ms <= 0) this.value = to
  }

  /** Jump without easing (first build, tests). */
  jump(v: number): void {
    this.value = this.from = this.to = v
  }

  /** Advance to time `now` (ms); true while the value is still moving. */
  step(now: number): boolean {
    if (this.value === this.to) return false
    const p = this.ms <= 0 ? 1 : Math.min(1, Math.max(0, (now - this.t0) / this.ms))
    this.value = p >= 1 ? this.to : this.from + (this.to - this.from) * bezier(this.curve, p)
    return this.value !== this.to
  }
}

export const smooth01 = (x: number, lo: number, hi: number): number => {
  const t = Math.min(1, Math.max(0, (x - lo) / (hi - lo)))
  return t * t * (3 - 2 * t)
}

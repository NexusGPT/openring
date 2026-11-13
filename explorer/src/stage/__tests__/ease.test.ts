import { afterEach, describe, expect, it, vi } from 'vitest'
import { Tween, bezier, motionTokens, reducedMotion, smooth01 } from '../ease'

afterEach(() => {
  vi.unstubAllGlobals()
  document.documentElement.removeAttribute('style')
})

describe('one easing', () => {
  it('takes duration and curve from the motion tokens, with a fallback', () => {
    expect(motionTokens().ms).toBe(320)
    document.documentElement.style.setProperty('--t-slow', '500ms')
    document.documentElement.style.setProperty('--ease-settle', 'cubic-bezier(0.1, 0.2, 0.3, 0.4)')
    expect(motionTokens()).toEqual({ ms: 500, curve: [0.1, 0.2, 0.3, 0.4] })
  })
  it('the curve starts at 0, ends at 1 and rises', () => {
    const c = motionTokens().curve
    expect(bezier(c, 0)).toBeCloseTo(0, 5)
    expect(bezier(c, 1)).toBeCloseTo(1, 5)
    expect(bezier(c, 0.5)).toBeGreaterThan(0.5) // ease-out
  })
  it('a tween ends exactly on its goal, in many frames, rising monotonically', () => {
    const t = new Tween(0)
    t.set(1, 1000)
    const seen: number[] = []
    for (let now = 1000; now <= 1400; now += 16) {
      t.step(now)
      seen.push(t.value)
    }
    expect(t.value).toBe(1)
    expect(seen.length).toBeGreaterThan(15)
    expect(seen.every((v, i) => i === 0 || v >= (seen[i - 1] as number))).toBe(true)
    expect(Math.max(...seen.map((v, i) => (i ? v - (seen[i - 1] as number) : 0)))).toBeLessThan(0.5)
  })
  it('a new goal restarts from where the value is (a dragged control is followed without steps)', () => {
    const t = new Tween(0)
    t.set(1, 0)
    t.step(100)
    const mid = t.value
    t.set(0.2, 100)
    t.step(116)
    expect(Math.abs(t.value - mid)).toBeLessThan(Math.abs(mid - 0.2) * 0.5) // moves toward the new goal, does not jump to it
    for (let now = 132; now < 600; now += 16) t.step(now)
    expect(t.value).toBe(0.2)
  })
  it('with prefers-reduced-motion every change is instant', () => {
    vi.stubGlobal('matchMedia', (q: string) => ({ matches: q.includes('reduce'), media: q }))
    expect(reducedMotion()).toBe(true)
    const t = new Tween(0)
    t.set(1, 0)
    expect(t.value).toBe(1)
  })
  it('smooth01 is 0 below, 1 above, smooth between', () => {
    expect([smooth01(0, 0, 0.25), smooth01(0.25, 0, 0.25), smooth01(0.125, 0, 0.25)]).toEqual([0, 1, 0.5])
  })
})

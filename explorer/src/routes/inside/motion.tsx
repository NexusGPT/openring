// Motion of the Inside panel. Every duration comes from the shell's tokens (--t-fast, --t-med, --t-slow);
// under prefers-reduced-motion the timers here are zero and primitives.css kills the CSS transitions.
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'

export const reducedMotion = (): boolean => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches
/** Mirrors --t-slow in tokens.css (320 ms); the leave step is a half of it. */
export const LEAVE_MS = 160
const easeOut = (t: number): number => 1 - Math.pow(1 - t, 3)

/** A number that can be set at once (a drag) or animated to a target (a click). */
export function useAnimatedValue(initial: number): [number, (v: number) => void, (v: number, ms?: number) => void] {
  const [value, setValue] = useState(initial)
  const raf = useRef(0)
  const cur = useRef(initial)
  const stop = () => cancelAnimationFrame(raf.current)
  const set = useCallback((v: number) => {
    stop()
    cur.current = v
    setValue(v)
  }, [])
  const animateTo = useCallback((target: number, ms = 640) => {
    stop()
    const from = cur.current
    if (reducedMotion() || from === target) {
      cur.current = target
      setValue(target)
      return
    }
    const t0 = performance.now()
    const step = (now: number) => {
      const t = Math.min(1, (now - t0) / ms)
      cur.current = from + (target - from) * easeOut(t)
      setValue(cur.current)
      if (t < 1) raf.current = requestAnimationFrame(step)
    }
    raf.current = requestAnimationFrame(step)
  }, [])
  useEffect(() => stop, [])
  return [value, set, animateTo]
}

/** Holds the content of one slot. When `k` changes the old content fades out (and drops 8 px), then the new
 *  content fades in and rises 8 px; `k` null means empty. Only one child is in the page at any time. */
export function Presence({ k, children, testid }: { k: string | null; children: ReactNode; testid?: string }) {
  const [shown, setShown] = useState<string | null>(k)
  const last = useRef<ReactNode>(children)
  const leaving = shown !== k
  if (!leaving) last.current = children
  useEffect(() => {
    if (shown === k) return
    const t = setTimeout(() => setShown(k), reducedMotion() ? 0 : LEAVE_MS)
    return () => clearTimeout(t)
  }, [k, shown])
  if (shown === null) return null
  return (
    <div key={shown} className="in-pres" data-phase={leaving ? 'out' : 'in'} data-testid={testid}>
      {leaving ? last.current : children}
    </div>
  )
}

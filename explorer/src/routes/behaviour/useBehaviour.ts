// The live session of the virtual ring: the log of presses, a clock, and the engine's output at "now".
// Pointer, keyboard and presses on the 3D ring all end up in press() / release().
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { FirmwareRules } from '../../contract'
import { EMPTY, run, type EngineOutput, type RingEvent } from './engine'

export interface Behaviour {
  out: EngineOutput
  now: number
  pressed: boolean
  press(source: string): void
  release(source: string): void
  /** a press that turned out to be a drag on the ring: forget it */
  cancel(source: string): void
  joystick(direction: string): void
}

export function useBehaviour(rules: FirmwareRules | null): Behaviour {
  const [events, setEvents] = useState<RingEvent[]>([])
  const [now, setNow] = useState(() => performance.now())
  const source = useRef<string | null>(null)
  const [pressed, setPressed] = useState(false)

  const out = useMemo(() => (rules ? run(rules, events, now) : EMPTY), [rules, events, now])
  const busy = pressed || out.recordingMs !== null

  useEffect(() => {
    if (!busy) return
    let raf = 0
    // a timer as well as the frame loop: a busy page may starve frames, and the ring must still fill
    const iv = window.setInterval(() => setNow(performance.now()), pressed ? 50 : 200)
    if (pressed) {
      const tick = () => {
        setNow(performance.now())
        raf = requestAnimationFrame(tick)
      }
      raf = requestAnimationFrame(tick)
    }
    return () => {
      cancelAnimationFrame(raf)
      window.clearInterval(iv)
    }
  }, [busy, pressed])

  const press = useCallback((s: string) => {
    if (source.current) return
    source.current = s
    const t = performance.now()
    setNow(t)
    setPressed(true)
    setEvents((e) => [...e, { kind: 'press', t }])
  }, [])
  const release = useCallback((s: string) => {
    if (source.current !== s) return
    source.current = null
    const t = performance.now()
    setNow(t)
    setPressed(false)
    setEvents((e) => [...e, { kind: 'release', t }])
  }, [])
  const cancel = useCallback((s: string) => {
    if (source.current !== s) return
    source.current = null
    setPressed(false)
    setEvents((e) => (e.length && e[e.length - 1]!.kind === 'press' ? e.slice(0, -1) : e))
  }, [])
  const joystick = useCallback((direction: string) => {
    const t = performance.now()
    setNow(t)
    setEvents((e) => [...e, { kind: 'joystick', t, direction }])
  }, [])

  return { out, now, pressed, press, release, cancel, joystick }
}


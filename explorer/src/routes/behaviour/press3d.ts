// A press on the joystick of the 3D ring (its centre press). The stage reports only clicks, so a hold is read here from
// the stage's own test API: the pointer must go down on the joystick's visible point (`screenPos`) and
// stay there; moving away is a drag that turns the ring, and the press is forgotten.
import { useEffect } from 'react'
import type { Behaviour } from './useBehaviour'
import { PRESS_NODE } from './nodes'

const REACH_PX = 34
const DRAG_PX = 6

export function useRingPress(b: Pick<Behaviour, 'press' | 'release' | 'cancel'>, enabled: boolean): void {
  const { press, release, cancel } = b
  useEffect(() => {
    if (!enabled) return
    const host = document.querySelector<HTMLElement>('[data-testid="app.stage"]')
    if (!host) return
    let from: { x: number; y: number } | null = null
    const near = (e: PointerEvent): boolean => {
      const canvas = host.querySelector('canvas') ?? host
      const p = window.__stage?.screenPos(PRESS_NODE)
      if (!p) return false
      const r = canvas.getBoundingClientRect()
      return Math.hypot(e.clientX - (r.left + p.x), e.clientY - (r.top + p.y)) <= REACH_PX
    }
    const down = (e: PointerEvent) => {
      if (e.button !== 0 || !near(e)) return
      from = { x: e.clientX, y: e.clientY }
      press('ring')
    }
    const move = (e: PointerEvent) => {
      if (from && Math.hypot(e.clientX - from.x, e.clientY - from.y) > DRAG_PX) {
        from = null
        cancel('ring')
      }
    }
    const up = () => {
      if (!from) return
      from = null
      release('ring')
    }
    host.addEventListener('pointerdown', down, true)
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', up)
    window.addEventListener('pointercancel', up)
    return () => {
      host.removeEventListener('pointerdown', down, true)
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', up)
      window.removeEventListener('pointercancel', up)
      cancel('ring')
    }
  }, [enabled, press, release, cancel])
}

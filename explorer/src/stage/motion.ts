// Per-frame motion of the stage: the eased explode, isolation fade and outline, the lid, the camera moves,
// orbit damping. Every value that eases is a Tween (ease.ts), so a frame in between is an in-between state.
import { Tween } from './ease'
import type { InnerState } from './inner'
import type { StageView } from './view'

export const LID_MS = 600

export interface Motion {
  explode: Tween
  /** exterior -> inside cross-fade level */
  appear: Tween
  iso: Tween
  select: Tween
  /** layer being isolated (kept while the fade runs back to 0) and the node whose outline is shown */
  isolated: string | null
  selectedShown: string | null
  /** case lid angle per view, eased in LID_MS */
  lid: Map<string, Tween>
}

export const newMotion = (): Motion => ({ explode: new Tween(0), appear: new Tween(0), iso: new Tween(0), select: new Tween(0), isolated: null, selectedShown: null, lid: new Map() })

export const innerState = (m: Motion): InnerState => ({ explode: m.explode.value, appear: m.appear.value, iso: m.iso.value, isolated: m.isolated, select: m.select.value, selected: m.selectedShown })

/** Advance everything to time `now` (ms). `moving`: eased values, camera moves, lid. `orbit`: the orbit controls moved
 *  (auto-rotate or damping): an ambient change the engine may draw at a lower rate. */
export function stepMotion(m: Motion, views: Iterable<StageView>, now: number): { moving: boolean; orbit: boolean } {
  let orbit = false
  let moving = m.explode.step(now)
  moving = m.appear.step(now) || moving
  moving = m.iso.step(now) || moving
  moving = m.select.step(now) || moving
  if (m.iso.value === 0 && m.iso.goal === 0) m.isolated = null
  if (m.select.value === 0 && m.select.goal === 0) m.selectedShown = null
  for (const v of views) {
    if (v.state !== 'ok') continue
    if (moving || v.inner) v.applyMotion(innerState(m))
    moving = v.stepAnim(now) || moving
    const lid = m.lid.get(v.spec.id)
    if (lid && (lid.step(now) || lid.value !== v.lidNow)) {
      v.applyLid(lid.value)
      moving = true
    }
    if (v.controls.update()) orbit = true
  }
  return { moving, orbit }
}

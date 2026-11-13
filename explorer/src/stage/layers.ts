// Explode by layer. Order, labels and z ranges come from part-placements.layers. The direction of
// a layer is the record's optional `explode` (a vector in design coordinates, or 'radial'). Without
// it the direction is derived from where the layer's parts sit around the band axis:
//   parts on one side of the axis (a block, a stack)  -> one direction for the whole layer
//   parts spread around the band                      -> each part moves outward along its own radius
// Layers that open in one direction travel so that, fully open, the clear space between the boxes of
// neighbouring layers is at least EXPLODE_MIN_GAP_MM, whatever their closed overlap.
import * as THREE from 'three'
import { EXPLODE_MIN_GAP_MM } from '../contract/constants'
import type { LayerRecord } from './types'
import { restBox } from './ghost'
import type { Part } from './nodes'

const SPREAD_LIMIT = 0.35 // mean radial vector shorter than this = parts spread around the band

/** design coordinates (x, y, z up) to three (x, z, -y) */
export const toThree = (v: { x: number; y: number; z: number }): THREE.Vector3 => new THREE.Vector3(v.x, v.z, -v.y)
export const toDesign = (v: THREE.Vector3): [number, number, number] => [v.x, -v.z, v.y]

export interface LayerPlan {
  id: string
  rank: number
  /** mm the layer moves along `dir` (or the radial base) when fully open */
  travel: number
  /** one direction for the whole layer, or null = per-part radial */
  dir: THREE.Vector3 | null
}

function radial(centre: THREE.Vector3, axisY: number): THREE.Vector3 {
  const v = new THREE.Vector3(0, centre.y - axisY, centre.z)
  return v.lengthSq() < 1e-6 ? new THREE.Vector3(0, 1, 0) : v.normalize()
}

/** Extent of a layer's rest boxes along a direction: [min, max]. */
function extentAlong(ps: readonly Part[], d: THREE.Vector3): [number, number] | null {
  let lo = Infinity
  let hi = -Infinity
  for (const p of ps) {
    const b = restBox(p)
    for (const x of [b.min.x, b.max.x]) for (const y of [b.min.y, b.max.y]) for (const z of [b.min.z, b.max.z]) {
      const t = new THREE.Vector3(x, y, z).dot(d)
      lo = Math.min(lo, t)
      hi = Math.max(hi, t)
    }
  }
  return lo <= hi ? [lo, hi] : null
}

/** Layers that open in one direction travel so the clear space between neighbours (from their real boxes, however
 *  much they overlap closed) is at least EXPLODE_MIN_GAP_MM when fully open. `rank` still orders radial layers. */
export function planLayers(layers: readonly LayerRecord[], partsByLayer: ReadonlyMap<string, Part[]>, axisY: number): LayerPlan[] {
  const sorted = [...layers].sort((a, b) => a.order - b.order)
  const used = new Map<string, number>() // direction group -> layers already placed
  const last = new Map<string, { travel: number; max: number | null }>()
  return sorted.map((l) => {
    const ps = partsByLayer.get(l.id) ?? []
    const dir = directionOf(l, ps, axisY)
    const group = dir ? dir.toArray().map((x) => x.toFixed(2)).join(',') : 'radial'
    const rank = (used.get(group) ?? 0) + 1
    used.set(group, rank)
    if (!dir) return { id: l.id, rank, dir, travel: rank * EXPLODE_MIN_GAP_MM }
    const ext = extentAlong(ps, dir)
    const prev = last.get(group)
    let travel = EXPLODE_MIN_GAP_MM // the first layer of a direction opens one gap from rest
    if (prev) {
      const clearance = ext && prev.max !== null ? ext[0] - prev.max : 0
      travel = Math.max(prev.travel, prev.travel + EXPLODE_MIN_GAP_MM - clearance)
    }
    last.set(group, { travel, max: ext ? ext[1] : null })
    return { id: l.id, rank, dir, travel }
  })
}

function directionOf(l: LayerRecord, ps: Part[], axisY: number): THREE.Vector3 | null {
  const given = l.explode
  if (given === 'radial') return null
  if (given && typeof given === 'object') {
    const d = toThree(given)
    return d.lengthSq() > 0 ? d.normalize() : new THREE.Vector3(0, 1, 0)
  }
  if (!ps.length) return new THREE.Vector3(0, 1, 0)
  const sum = new THREE.Vector3()
  for (const p of ps) sum.add(radial(p.obj.userData.restCentre ?? new THREE.Box3().setFromObject(p.obj).getCenter(new THREE.Vector3()), axisY))
  sum.divideScalar(ps.length)
  return sum.length() < SPREAD_LIMIT ? null : sum.normalize()
}

const SAME_RADIUS_DEG = 12

/** For parts of a per-part-radial layer: how many parts of the same radius lie nearer the axis (0 = nearest).
 *  Each such part opens one more gap, so the parts along one radius never hide each other. */
export function spreadIndex(parts: readonly Part[], axisY: number): Map<string, number> {
  const polar = parts.map((p) => {
    const c = (p.obj.userData.restCentre ?? new THREE.Box3().setFromObject(p.obj).getCenter(new THREE.Vector3())) as THREE.Vector3
    return { name: p.name, angle: Math.atan2(c.z, c.y - axisY), dist: Math.hypot(c.y - axisY, c.z) }
  })
  const tol = (SAME_RADIUS_DEG * Math.PI) / 180
  const diff = (a: number, b: number) => Math.abs(Math.atan2(Math.sin(a - b), Math.cos(a - b)))
  const out = new Map<string, number>()
  for (const p of polar) out.set(p.name, polar.filter((q) => q !== p && diff(q.angle, p.angle) <= tol && q.dist < p.dist).length)
  return out
}

/** World-space displacement (mm) of one part for an explode value 0..1. `extra` = spreadIndex for per-part radial layers. */
export function displacement(plan: LayerPlan, centre: THREE.Vector3, axisY: number, explode: number, extra = 0): THREE.Vector3 {
  const dir = plan.dir ?? radial(centre, axisY)
  return dir.clone().multiplyScalar((plan.dir ? plan.travel : (plan.rank + extra) * EXPLODE_MIN_GAP_MM) * explode)
}

/** Move a part by a world-space offset from its rest position (rest is stored on first use). */
export function placeOffset(obj: THREE.Object3D, offsetWorld: THREE.Vector3): void {
  const rest = (obj.userData.rest ??= obj.position.clone()) as THREE.Vector3
  obj.parent?.updateWorldMatrix(true, false)
  const inv = new THREE.Matrix3().setFromMatrix4((obj.parent?.matrixWorld ?? new THREE.Matrix4()).clone().invert())
  obj.position.copy(rest).add(offsetWorld.clone().applyMatrix3(inv))
  obj.updateMatrixWorld(true)
}

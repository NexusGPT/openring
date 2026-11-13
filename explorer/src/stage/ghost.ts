// Enclosures: the body and any skin that wraps other parts. When the ring is open they are drawn as
// ghosts so the parts inside can be seen and clicked. A layer may say so (`ghost_when_open`); without
// that, a part is an enclosure when its box holds the centres of more than half of the other parts.
import * as THREE from 'three'
import type { Part } from './nodes'

export const GHOST_OPEN = 0.15 // explode value above which enclosures ghost
export const GHOST_OPACITY = 0.12

export const restBox = (p: Part): THREE.Box3 => (p.obj.userData.restBox as THREE.Box3 | undefined) ?? new THREE.Box3().setFromObject(p.obj)
const restCentre = (p: Part): THREE.Vector3 => (p.obj.userData.restCentre as THREE.Vector3 | undefined) ?? restBox(p).getCenter(new THREE.Vector3())

/** `flags`: the layers' `ghost_when_open` where the record has it (layer id -> true/false); `partFlags`: the same per part
 *  (part name -> true/false), which wins over the layer's. */
export function enclosureSet(parts: readonly Part[], flags: ReadonlyMap<string, boolean | undefined>, partFlags: ReadonlyMap<string, boolean> = new Map()): Set<string> {
  const out = new Set<string>()
  for (const p of parts) {
    const flag = partFlags.get(p.name) ?? (p.layer ? flags.get(p.layer) : undefined)
    if (flag !== undefined) {
      if (flag) out.add(p.name)
      continue
    }
    const others = parts.filter((q) => q !== p)
    if (!others.length) continue
    const box = restBox(p)
    const inside = others.filter((q) => box.containsPoint(restCentre(q))).length
    if (inside > others.length / 2) out.add(p.name)
  }
  return out
}

/** Solid volume of a closed mesh in world units (signed tetrahedra; the sign of the winding does not matter). */
export function meshVolume(m: THREE.Mesh): number {
  const pos = m.geometry.attributes.position
  if (!pos) return 0
  const idx = m.geometry.index
  const n = idx ? idx.count : pos.count
  const a = new THREE.Vector3()
  const b = new THREE.Vector3()
  const c = new THREE.Vector3()
  let v = 0
  for (let i = 0; i < n; i += 3) {
    a.fromBufferAttribute(pos, idx ? idx.getX(i) : i)
    b.fromBufferAttribute(pos, idx ? idx.getX(i + 1) : i + 1)
    c.fromBufferAttribute(pos, idx ? idx.getX(i + 2) : i + 2)
    v += a.dot(b.cross(c)) / 6
  }
  return Math.abs(v) * Math.abs(m.matrixWorld.determinant())
}

export const THIN_SHELL = 0.2 // solid volume under this share of the box volume = a thin shell

/** A part whose solid volume is under THIN_SHELL of its box volume (a liner, a skin, a curved pouch). */
export function isThinShell(p: Part): boolean {
  const s = restBox(p).getSize(new THREE.Vector3())
  const box = s.x * s.y * s.z
  return box > 0 && p.meshes.reduce((t, m) => t + meshVolume(m), 0) < box * THIN_SHELL
}

/** Thin shells that stand between the camera and some other part: a ray from the camera to sample points of the
 *  other part (its centre and eight points inside its box) meets the shell first. Of nested shells only the
 *  outermost ghosts (a shell covered by a larger shell stays solid), so the part behind the front
 *  skin can be clicked. Only the shells' own meshes are tested, so the cost stays small however heavy the model is. */
export function coveringShells(camera: THREE.Camera, shells: readonly Part[], others: readonly Part[]): Set<string> {
  const ray = new THREE.Raycaster()
  const from = camera.getWorldPosition(new THREE.Vector3())
  const vol = (q: Part): number => {
    const z = new THREE.Box3().setFromObject(q.obj).getSize(new THREE.Vector3())
    return z.x * z.y * z.z
  }
  const isShell = new Set(shells.map((x) => x.name))
  const covers = new Map<string, Set<string>>() // shell -> parts it covers
  const covered = new Set<string>() // parts covered by some shell
  for (const sh of shells) {
    const mine = new Set<string>()
    for (const q of others) {
      if (q === sh) continue
      if (isShell.has(q.name) && vol(sh) <= vol(q)) continue // a smaller shell does not cover a larger one: the outer skin is the front
      const b = new THREE.Box3().setFromObject(q.obj)
      const size = b.getSize(new THREE.Vector3())
      const pts = [b.getCenter(new THREE.Vector3())]
      for (const fx of [0.25, 0.75]) for (const fy of [0.25, 0.75]) for (const fz of [0.25, 0.75]) pts.push(b.min.clone().add(new THREE.Vector3(size.x * fx, size.y * fy, size.z * fz)))
      for (const pt of pts) {
        const dir = pt.clone().sub(from)
        const dist = dir.length()
        ray.set(from, dir.normalize())
        ray.far = dist - 1e-3
        if (ray.intersectObjects(sh.meshes, false).length) {
          mine.add(q.name)
          covered.add(q.name)
          break
        }
      }
    }
    covers.set(sh.name, mine)
  }
  return new Set(shells.filter((sh) => (covers.get(sh.name)?.size ?? 0) > 0 && !covered.has(sh.name)).map((sh) => sh.name))
}

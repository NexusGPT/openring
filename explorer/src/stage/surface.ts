// A point ON the visible surface of a part, for tests and journeys that must click it. The centre of a
// curved part's box can be empty space; this casts rays through the part's projected box and keeps the
// hit nearest the box centre where the part is the first thing the ray meets. A fully hidden part
// returns the nearest point of its own surface (the click then lands on whatever hides it).
import * as THREE from 'three'
import type { Part } from './nodes'

const GRID = 11

/** NDC point (-1..1) on the part's surface, or null when no ray meets the part at all. */
export function surfacePoint(camera: THREE.Camera, parts: ReadonlyMap<string, Part>, part: Part): THREE.Vector2 | null {
  const box = new THREE.Box3().setFromObject(part.obj)
  if (box.isEmpty()) return null
  camera.updateMatrixWorld(true)
  const centre = box.getCenter(new THREE.Vector3()).project(camera)
  const lo = new THREE.Vector2(1, 1)
  const hi = new THREE.Vector2(-1, -1)
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
    const p = new THREE.Vector3(x, y, z).project(camera)
    lo.set(Math.min(lo.x, p.x), Math.min(lo.y, p.y))
    hi.set(Math.max(hi.x, p.x), Math.max(hi.y, p.y))
  }
  const all = [...parts.values()].filter((p) => p.obj.visible && !p.ghost).flatMap((p) => p.meshes)
  const ray = new THREE.Raycaster()
  const visible = (x: number, y: number): boolean => {
    ray.setFromCamera(new THREE.Vector2(x, y), camera)
    const first = ray.intersectObjects(all, false)[0]
    return !!first && part.meshes.includes(first.object as THREE.Mesh)
  }
  // coarse to fine: most parts answer at the centre or the 3 x 3 grid, so few rays are cast (heavy meshes make each ray dear)
  for (const n of [1, 3, 5, 9]) {
    const pts: Array<{ d: number; x: number; y: number }> = []
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const x = n === 1 ? centre.x : lo.x + ((hi.x - lo.x) * (i + 0.5)) / n
      const y = n === 1 ? centre.y : lo.y + ((hi.y - lo.y) * (j + 0.5)) / n
      pts.push({ d: Math.hypot(x - centre.x, y - centre.y), x, y })
    }
    pts.sort((p, q) => p.d - q.d)
    const hit = pts.find((p) => visible(p.x, p.y))
    if (hit) return new THREE.Vector2(hit.x, hit.y)
  }
  // fully hidden: the nearest point of the part's own surface (a click there lands on what hides it)
  let hidden: { d: number; p: THREE.Vector2 } | null = null
  for (let i = 0; i < GRID; i++) for (let j = 0; j < GRID; j++) {
    const x = lo.x + ((hi.x - lo.x) * (i + 0.5)) / GRID
    const y = lo.y + ((hi.y - lo.y) * (j + 0.5)) / GRID
    ray.setFromCamera(new THREE.Vector2(x, y), camera)
    const d = Math.hypot(x - centre.x, y - centre.y)
    if (ray.intersectObjects(part.meshes, false).length && (!hidden || d < hidden.d)) hidden = { d, p: new THREE.Vector2(x, y) }
  }
  const hit = hidden as { p: THREE.Vector2 } | null
  return hit ? hit.p : null
}

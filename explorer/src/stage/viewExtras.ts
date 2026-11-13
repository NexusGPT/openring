// What surrounds the model in an exterior view: the lit screen face, the light glow, the contact
// shadow, the finger and the 10 mm scale cue. Sizes and positions come from the records and the model.
import * as THREE from 'three'
import type { RingModel } from '../contract'
import { radialTexture } from './environment'
import type { KindMaterials } from './materials'
import type { Part } from './nodes'

const FINGER_GAP_MM = 0.4 // clearance between the finger and the underside of the block (seed: BORE_GAP)
export { FINGER_GAP_MM }

/** The contact shadow plane is SHADOW_W x the block width wide and SHADOW_D of that deep. */
export const SHADOW_W = 1.5
export const SHADOW_D = 0.54

const union = (parts: Part[]): THREE.Box3 => parts.reduce((b, p) => b.expandByObject(p.obj), new THREE.Box3())

const FACE_NX = 48
const FACE_NY = 24

/** Height of the glass surface above (x, z), the highest hit of a ray from above on the glass meshes; null where there is none. */
export function glassHeight(glass: THREE.Mesh[], x: number, z: number, from = 100): number | null {
  const ray = new THREE.Raycaster(new THREE.Vector3(x, from, z), new THREE.Vector3(0, -1, 0))
  const hit = ray.intersectObjects(glass, false)[0]
  return hit ? hit.point.y : null
}

const meshesOf = (parts: Map<string, Part>, kind: Part['kind']): THREE.Mesh[] => [...parts.values()].filter((p) => p.kind === kind).flatMap((p) => p.meshes)

/** With a glass in the view the screen solid is not drawn: the glass is one surface and the lit picture lies on it (a flat slab
 *  would stand proud of the domed glass and show its own end face and top). Its meshes stay in the part for picking. */
export function hideScreenUnderGlass(parts: Map<string, Part>): void {
  if (!meshesOf(parts, 'glass').length) return
  for (const m of meshesOf(parts, 'screen')) m.visible = false
}

/** The lit picture: the screen rectangle of the record (size, place), laid ON the glass surface (every vertex at the glass height,
 *  the material pulls it forward by depth offset). With no glass in the view it is a flat plane just above the screen solid. */
export function buildFace(ring: RingModel | null, parts: Map<string, Part>, mats: KindMaterials, scene: THREE.Scene): THREE.Mesh | null {
  const screens = [...parts.values()].filter((p) => p.kind === 'screen')
  if (!ring || !screens.length) return null
  const r = ring.screens.rect
  const flatY = union(screens).max.y + 0.02
  const glass = meshesOf(parts, 'glass')
  const geo = new THREE.PlaneGeometry(r.w, r.h, glass.length ? FACE_NX : 1, glass.length ? FACE_NY : 1)
  const plane = new THREE.Mesh(geo, mats.screenFace)
  plane.rotation.x = -Math.PI / 2
  if (glass.length) {
    glass.forEach((m) => m.updateWorldMatrix(true, false))
    const pos = geo.attributes.position as THREE.BufferAttribute
    for (let i = 0; i < pos.count; i++) {
      // local (x, y) -> world x = cx + x, z = -cy - y; local z becomes world y
      pos.setZ(i, glassHeight(glass, r.cx + pos.getX(i), -r.cy - pos.getY(i)) ?? flatY)
    }
    pos.needsUpdate = true
    geo.computeBoundingBox()
    geo.computeBoundingSphere()
    plane.position.set(r.cx, 0, -r.cy)
  } else plane.position.set(r.cx, flatY, -r.cy)
  plane.renderOrder = 2
  scene.add(plane)
  return plane
}

export function buildGlow(parts: Map<string, Part>, scene: THREE.Scene): THREE.Sprite | null {
  const lights = [...parts.values()].filter((p) => p.kind === 'light')
  if (!lights.length) return null
  const lb = union(lights)
  const c = lb.getCenter(new THREE.Vector3())
  const map = radialTexture([[0, 'rgba(255,70,50,0.95)'], [0.25, 'rgba(255,40,30,0.4)'], [1, 'rgba(255,0,0,0)']])
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false }))
  sp.scale.setScalar(3)
  sp.position.set(c.x, lb.max.y + 0.1, c.z)
  sp.visible = false
  scene.add(sp)
  return sp
}

export function buildShadows(whole: THREE.Box3, block: THREE.Box3, scene: THREE.Scene): THREE.Mesh[] {
  const floorY = whole.min.y - 0.05
  const sx = (block.max.x - block.min.x) * SHADOW_W
  const tex = radialTexture([[0, 'rgba(0,0,0,0.55)'], [0.35, 'rgba(0,0,0,0.25)'], [1, 'rgba(0,0,0,0)']])
  const mk = (w: number, d: number, y: number) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, toneMapped: false }))
    m.rotation.x = -Math.PI / 2
    m.position.set((whole.min.x + whole.max.x) / 2, y, 0)
    m.scale.set(w, d, 1)
    m.renderOrder = -1
    scene.add(m)
    return m
  }
  return [mk(sx, sx * SHADOW_D, floorY), mk(sx * 0.38, sx * 0.38 * SHADOW_D, floorY + 0.01)]
}

/** A finger cylinder coaxial with the band, and a 10 mm scale line with end ticks. Both start hidden. */
export function buildFinger(block: THREE.Box3, axisY: number, innerD: number, scene: THREE.Scene): { finger: THREE.Mesh; cue: THREE.Group } | null {
  if (innerD <= 0) return null
  const skin = new THREE.MeshPhysicalMaterial({ color: 0xd9a688, roughness: 0.55, metalness: 0, clearcoat: 0.1, sheen: 0.4 })
  const finger = new THREE.Mesh(new THREE.CylinderGeometry(innerD / 2, innerD / 2, 600, 96, 1), skin)
  finger.rotation.z = Math.PI / 2 // along X, the band's axis
  finger.position.set(0, axisY, 0)
  finger.visible = false
  const cue = new THREE.Group()
  const cm = new THREE.MeshBasicMaterial({ color: 0x120804, depthTest: false, transparent: true })
  for (const [w, h, x] of [[10, 0.06, 0], [0.06, 0.8, -5], [0.06, 0.8, 5]] as const) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.05), cm)
    m.position.set(x, 0, 0)
    m.renderOrder = 10
    cue.add(m)
  }
  cue.position.set(block.min.x - 8.35, block.min.y - 0.9, 2.5)
  cue.visible = false
  scene.add(finger, cue)
  return { finger, cue }
}

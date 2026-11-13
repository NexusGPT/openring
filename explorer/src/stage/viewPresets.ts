// Camera presets, ported from the seed viewer: a target, a direction and a radius to fit.
import * as THREE from 'three'
import type { ViewPreset } from './types'

export interface Framing {
  whole: THREE.Box3
  /** the object and its contact shadow: everything that must stay inside the margin */
  fit: THREE.Box3
  block: THREE.Box3
  /** y of the band axis (the finger axis) */
  axisY: number
  /** inner diameter of the band, mm */
  innerD: number
}

export interface Pose {
  target: THREE.Vector3
  dir: THREE.Vector3
  r: number
}

/** Radius of the sphere around `target` that holds the whole box (its farthest corner). */
export function radiusAround(box: THREE.Box3, target: THREE.Vector3): number {
  const far = new THREE.Vector3(Math.max(Math.abs(box.min.x - target.x), Math.abs(box.max.x - target.x)), Math.max(Math.abs(box.min.y - target.y), Math.abs(box.max.y - target.y)), Math.max(Math.abs(box.min.z - target.z), Math.abs(box.max.z - target.z)))
  return far.length()
}

export function presetPose(f: Framing, name: ViewPreset): Pose {
  const wc = f.whole.getCenter(new THREE.Vector3())
  const bc = f.block.getCenter(new THREE.Vector3())
  const height = f.whole.max.y - f.whole.min.y
  const pose = (target: THREE.Vector3, dir: THREE.Vector3, box: THREE.Box3): Pose => ({ target, dir, r: radiusAround(box, target) })
  switch (name) {
    case 'top':
      return pose(bc, new THREE.Vector3(0, 1, 0.16), f.whole)
    case 'side':
      return pose(wc, new THREE.Vector3(1, 0.1, 0), f.fit)
    case 'finger':
      return { target: new THREE.Vector3(f.whole.min.x * 0.55, f.axisY * 0.6, 0), dir: new THREE.Vector3(0.7, 0.42, 1), r: f.innerD * 1.6 }
    default:
      return pose(wc.clone().add(new THREE.Vector3(0, 0.22 * height, 0)), new THREE.Vector3(0.85, 0.58, 1), f.fit)
  }
}

/** Share of the smaller screen dimension a fitted sphere may fill: 12 % of margin on each side. */
export const FILL = 0.76

/** Distance at which a sphere of radius r fills FILL of the smaller field of view, whatever the aspect. */
export function fitDistance(cam: THREE.PerspectiveCamera, r: number): number {
  const v = THREE.MathUtils.degToRad(cam.fov) / 2
  const h = Math.atan(Math.tan(v) * cam.aspect)
  return r / Math.sin(Math.atan(FILL * Math.tan(Math.min(v, h))))
}

/** Largest share of the screen's half-extent the box reaches (0 centre .. 1 edge) over the 8 corners. */
export function reach(cam: THREE.PerspectiveCamera, box: THREE.Box3): number {
  cam.updateMatrixWorld(true)
  let m = 0
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
    const p = new THREE.Vector3(x, y, z).project(cam)
    m = Math.max(m, Math.abs(p.x), Math.abs(p.y))
  }
  return m
}

export function poseCamera(cam: THREE.PerspectiveCamera, p: Pose): { pos: THREE.Vector3; target: THREE.Vector3 } {
  return { pos: p.target.clone().add(p.dir.clone().normalize().multiplyScalar(fitDistance(cam, p.r))), target: p.target.clone() }
}

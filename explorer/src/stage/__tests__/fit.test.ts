import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { fitDistance, poseCamera, presetPose, reach, type Framing } from '../viewPresets'
import type { ViewPreset } from '../types'

const box = (x: number, y: number, z: number, y0 = 0) => new THREE.Box3(new THREE.Vector3(-x / 2, y0, -z / 2), new THREE.Vector3(x / 2, y0 + y, z / 2))
// a slab, and a ring-like object (block on a band); the shadow is a flat box under each
const slab = (): Framing => {
  const whole = box(29.3, 3.2, 14.75)
  const fit = whole.clone().union(new THREE.Box3(new THREE.Vector3(-22, -0.05, -6), new THREE.Vector3(22, 0, 6)))
  return { whole, block: whole.clone(), fit, axisY: -9.9, innerD: 18.95 }
}
const ring = (): Framing => {
  const whole = new THREE.Box3(new THREE.Vector3(-14.65, -21.95, -12.1), new THREE.Vector3(14.65, 3.2, 12.1))
  const fit = whole.clone().union(new THREE.Box3(new THREE.Vector3(-22, -22, -6), new THREE.Vector3(22, -21.95, 6)))
  return { whole, block: new THREE.Box3(new THREE.Vector3(-14.65, 0, -7.4), new THREE.Vector3(14.65, 3.2, 7.4)), fit, axisY: -9.9, innerD: 18.95 }
}
const stages: Array<[string, number, number]> = [['1440x900 panel closed', 875, 845], ['1280x800', 770, 745], ['panel widened', 520, 845], ['wide', 1400, 800]]

describe('fit: the object and its shadow stay 12 % inside the stage', () => {
  for (const [name, f] of [['slab', slab], ['ring', ring]] as const) {
    for (const preset of ['three-quarter', 'top', 'side'] as ViewPreset[]) {
      for (const [sn, w, h] of stages) {
        it(`${name}, ${preset}, ${sn}, every azimuth`, () => {
          const fr = f()
          const cam = new THREE.PerspectiveCamera(28, w / h, 1, 2000)
          const { pos, target } = poseCamera(cam, presetPose(fr, preset))
          const off = pos.clone().sub(target)
          const polar = Math.hypot(off.x, off.z)
          const worst = Math.max(...[0, 45, 90, 135, 180, 270].map((deg) => {
            const a = Math.atan2(off.z, off.x) + (deg * Math.PI) / 180
            cam.position.set(target.x + polar * Math.cos(a), target.y + off.y, target.z + polar * Math.sin(a))
            cam.lookAt(target)
            return reach(cam, preset === 'top' ? fr.whole : fr.fit)
          }))
          expect(worst).toBeLessThanOrEqual(0.76 + 1e-6)
        })
      }
    }
  }
  it('a camera that is too close fails the measure (the check can fail)', () => {
    const fr = slab()
    const cam = new THREE.PerspectiveCamera(28, 1, 1, 2000)
    const { pos, target } = poseCamera(cam, presetPose(fr, 'three-quarter'))
    cam.position.copy(target).add(pos.clone().sub(target).multiplyScalar(0.7))
    cam.lookAt(target)
    expect(reach(cam, fr.fit)).toBeGreaterThan(0.76)
    expect(fitDistance(cam, 10)).toBeGreaterThan(10)
  })
})

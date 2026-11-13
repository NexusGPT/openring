import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { coveringShells, isThinShell, meshVolume } from '../ghost'
import { APPEAR_AT, InnerRing, type InnerState } from '../inner'
import type { Part } from '../nodes'
import type { NodeSpec } from '../types'

// a closed thin-walled cup (a liner): outer wall 10, inner wall 9.5, height 10, axis along y
function cup(): THREE.Mesh {
  const pts = [[10, 0], [10, 10], [9.5, 10], [9.5, 0], [10, 0]].map(([x, y]) => new THREE.Vector2(x, y))
  const m = new THREE.Mesh(new THREE.LatheGeometry(pts, 48), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }))
  m.updateMatrixWorld(true)
  return m
}
const block = (at: [number, number, number]) => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(4, 4, 4), new THREE.MeshBasicMaterial())
  m.position.set(...at)
  m.updateMatrixWorld(true)
  return m
}
const part = (name: string, obj: THREE.Mesh): Part => {
  const b = new THREE.Box3().setFromObject(obj)
  obj.userData.restBox = b
  obj.userData.restCentre = b.getCenter(new THREE.Vector3())
  return { name, obj, meshes: [obj], kind: 'plain', layer: null }
}

describe('thin shells that cover a part', () => {
  it('a thin-walled cup is a thin shell, a block is not', () => {
    expect(meshVolume(cup())).toBeGreaterThan(250)
    expect(isThinShell(part('liner', cup()))).toBe(true)
    expect(isThinShell(part('b', block([0, 0, 0])))).toBe(false)
  })
  it('it covers a block inside it from a camera outside, not a block far away on the camera side', () => {
    const liner = part('liner', cup())
    const inside = part('inside', block([6, 5, 0]))
    const near = part('near', block([0, 5, 60]))
    const cam = new THREE.PerspectiveCamera(28, 1, 1, 500)
    cam.position.set(0, 5, 90)
    cam.lookAt(0, 5, 0)
    expect([...coveringShells(cam, [liner], [inside])]).toEqual(['liner'])
    expect(coveringShells(cam, [liner], [near]).size).toBe(0)
  })
  it('of two nested shells only the front one ghosts, so the part behind it can be clicked', () => {
    const outer = part('outer', cup())
    const smallGeo = new THREE.LatheGeometry([[6, 0], [6, 10], [5.5, 10], [5.5, 0], [6, 0]].map(([x, y]) => new THREE.Vector2(x, y)), 48)
    const innerCup = new THREE.Mesh(smallGeo, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }))
    innerCup.updateMatrixWorld(true)
    const inner = part('inner', innerCup)
    const core = part('core', block([0, 5, 0]))
    const cam = new THREE.PerspectiveCamera(28, 1, 1, 500)
    cam.position.set(0, 5, 90)
    cam.lookAt(0, 5, 0)
    expect([...coveringShells(cam, [outer, inner], [outer, inner, core])]).toEqual(['outer'])
  })
  it('the ring draws the covering shell as a ghost when open; a part flag false keeps it solid, true makes any part a ghost', () => {
    const build = (flags: Map<string, boolean> = new Map()) => {
      const root = new THREE.Group()
      const liner = Object.assign(cup(), { name: 'liner' })
      const inside = Object.assign(block([6, 5, 0]), { name: 'inside' })
      const far = Object.assign(block([40, 5, 0]), { name: 'far' })
      root.add(liner, inside, far)
      root.updateMatrixWorld(true)
      const specs: NodeSpec[] = [{ name: 'liner', kind: 'plain' }, { name: 'inside', kind: 'plain' }, { name: 'far', kind: 'plain' }]
      const ring = new InnerRing(root, specs, [], -10, false, flags)
      const cam = new THREE.PerspectiveCamera(28, 1, 1, 500)
      cam.position.set(0, 5, 90)
      cam.lookAt(0, 5, 0)
      cam.updateMatrixWorld(true)
      ring.updateCover(cam)
      const st: InnerState = { explode: 1, appear: 1, iso: 0, isolated: null, select: 0, selected: null }
      for (let i = 0; i < 40; i++) ring.apply(st) // the cover fades in over a few frames
      return ring
    }
    expect(build().parts.get('liner')?.opacity).toBeCloseTo(0.12, 1)
    expect(build().parts.get('far')?.opacity).toBe(1)
    expect(build(new Map([['liner', false]])).parts.get('liner')?.opacity).toBe(1)
    expect(build(new Map([['far', true]])).parts.get('far')?.opacity).toBeCloseTo(0.12, 1)
    expect(APPEAR_AT).toBe(0.25)
  })
})

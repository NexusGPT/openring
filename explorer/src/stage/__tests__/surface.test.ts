import * as THREE from 'three'
import { describe, expect, it, vi } from 'vitest'
import { surfacePoint } from '../surface'
import type { Part } from '../nodes'

// a flat ring seen face-on (like a cell curled in the band): the centre of its box is the hole
function curved(): { parts: Map<string, Part>; cam: THREE.PerspectiveCamera; cell: Part } {
  const geo = new THREE.RingGeometry(6, 10, 48)
  const mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }))
  mesh.updateMatrixWorld(true)
  const cell: Part = { name: 'cell', obj: mesh, meshes: [mesh], kind: 'plain', layer: null }
  const cam = new THREE.PerspectiveCamera(28, 1, 1, 500)
  cam.position.set(0, 0, 90)
  cam.lookAt(0, 0, 0)
  return { parts: new Map([['cell', cell]]), cam, cell }
}

describe('screenPos lands on the surface', () => {
  it("the centre of a curved part's box misses it, the returned point hits it", () => {
    const { parts, cam, cell } = curved()
    const c = new THREE.Box3().setFromObject(cell.obj).getCenter(new THREE.Vector3()).project(cam)
    const ray = new THREE.Raycaster()
    ray.setFromCamera(new THREE.Vector2(c.x, c.y), cam)
    expect(ray.intersectObjects(cell.meshes, false)).toHaveLength(0)
    const p = surfacePoint(cam, parts, cell)
    expect(p).not.toBeNull()
    ray.setFromCamera(p as THREE.Vector2, cam)
    expect(ray.intersectObjects(cell.meshes, false).length).toBeGreaterThan(0)
  })
  it('a part hidden behind another still gets a point on its own surface; nothing in view gives null', () => {
    const { parts, cam, cell } = curved()
    const wall = new THREE.Mesh(new THREE.BoxGeometry(60, 60, 1), new THREE.MeshBasicMaterial())
    wall.position.z = 50
    wall.updateMatrixWorld(true)
    parts.set('wall', { name: 'wall', obj: wall, meshes: [wall], kind: 'plain', layer: null })
    expect(surfacePoint(cam, parts, cell)).not.toBeNull()
    const none: Part = { name: 'none', obj: new THREE.Object3D(), meshes: [], kind: 'plain', layer: null }
    expect(surfacePoint(cam, parts, none)).toBeNull()
  })
})

describe('screenPos stays cheap on heavy models', () => {
  it('a part visible at the centre of its box costs one ray, not a grid', () => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(10, 10, 10), new THREE.MeshBasicMaterial())
    mesh.updateMatrixWorld(true)
    const part: Part = { name: 'block', obj: mesh, meshes: [mesh], kind: 'plain', layer: null }
    const cam = new THREE.PerspectiveCamera(28, 1, 1, 500)
    cam.position.set(0, 0, 90)
    cam.lookAt(0, 0, 0)
    const spy = vi.spyOn(THREE.Raycaster.prototype, 'intersectObjects')
    expect(surfacePoint(cam, new Map([['block', part]]), part)).not.toBeNull()
    expect(spy).toHaveBeenCalledTimes(1)
    spy.mockRestore()
  })
})

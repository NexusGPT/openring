// screen-face-C15: the lit rectangle has the size and place of the record, there is one face layer, and the glass is one material.
import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { RING } from './harness-data'
import { makeMaterials } from '../materials'
import type { Part } from '../nodes'
import { buildFace } from '../viewExtras'

const part = (name: string, kind: Part['kind'], min: [number, number, number], max: [number, number, number]): Part => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(max[0] - min[0], max[1] - min[1], max[2] - min[2]))
  m.position.set((min[0] + max[0]) / 2, (min[1] + max[1]) / 2, (min[2] + max[2]) / 2)
  m.updateMatrixWorld(true)
  return { name, obj: m, meshes: [m], kind, layer: null }
}

describe('the lit picture on the glass (screen-face-C15)', () => {
  const mats = makeMaterials(new THREE.Texture())
  const parts = new Map<string, Part>([
    ['glass', part('glass', 'glass', [-14, 2.75, -7], [14, 3.85, 7])],
    ['screen', part('screen', 'screen', [-9.3, 3.37, -5.4], [12.3, 3.87, 5.4])],
  ])

  it('C15a one face plane, of the size and place of the screen rectangle of the record', () => {
    const scene = new THREE.Scene()
    const face = buildFace(RING, parts, mats, scene)
    expect(face).not.toBeNull()
    const lit = scene.children.filter((o) => (o as THREE.Mesh).material === mats.screenFace)
    expect(lit).toHaveLength(1)
    const b = new THREE.Box3().setFromObject(face as THREE.Mesh)
    const s = b.getSize(new THREE.Vector3())
    expect([s.x, s.z].map((v) => +v.toFixed(3))).toEqual([RING.screens.rect.w, RING.screens.rect.h])
    const c = b.getCenter(new THREE.Vector3())
    expect(c.x).toBeCloseTo(RING.screens.rect.cx, 9)
    expect(Math.abs(c.z + RING.screens.rect.cy)).toBeLessThan(1e-9)
    expect(c.y).toBeCloseTo(3.85, 6) // on the glass surface, not on the slab that stands above it
  })
  it('C15b the picture is upright for a reader of the plan: its right is +x of the record, its top is +y of the record', () => {
    const scene = new THREE.Scene()
    const face = buildFace(RING, parts, mats, scene) as THREE.Mesh
    face.updateMatrixWorld(true)
    const at = (u: number, v: number) => new THREE.Vector3(u - 0.5, v - 0.5, 0).multiply(new THREE.Vector3(RING.screens.rect.w, RING.screens.rect.h, 1)).applyMatrix4(face.matrixWorld)
    const right = at(1, 0.5).sub(at(0, 0.5))
    const top = at(0.5, 1).sub(at(0.5, 0))
    expect(right.x).toBeGreaterThan(0) // along the finger, +x of the record
    expect(-top.z).toBeGreaterThan(0) // the scene's -z is the record's +y (thumb side)
  })
  it('C15e without a glass in the view the plane lies just above the screen solid, flat', () => {
    const b = new THREE.Box3().setFromObject(buildFace(RING, new Map([['screen', parts.get('screen') as Part]]), mats, new THREE.Scene()) as THREE.Mesh)
    expect(b.min.y).toBeCloseTo(3.89, 6)
    expect(b.max.y).toBeCloseTo(3.89, 6)
  })
  it('C15c no face without a screen solid or without the record, so there is never a second layer', () => {
    expect(buildFace(null, parts, mats, new THREE.Scene())).toBeNull()
    expect(buildFace(RING, new Map([['glass', parts.get('glass') as Part]]), mats, new THREE.Scene())).toBeNull()
  })
  it('C15d the screen solid and the glass solid are one material, so the glass has one gloss edge to edge; the lit picture adds light and replaces nothing', () => {
    expect(mats.byKind.screen).toBe(mats.byKind.glass)
    const m = mats.screenFace
    expect(m.blending).toBe(THREE.AdditiveBlending) // black pixels add nothing: no edge where the lit area ends
    expect(m.depthWrite).toBe(false)
    expect(m.toneMapped).toBe(false)
    expect(m.color.r).toBe(1) // the picture's own colours, not dimmed
  })
})

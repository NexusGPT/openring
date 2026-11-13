import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { RING } from './harness-data'
import { makeSlab, slabMaterial } from '../slab'
import { exteriorView, internalsView } from '../views'

describe('plain black slab', () => {
  it("has the block's true size, bottom at y = 0 (design x, y, z = three x, z, y)", () => {
    const g = makeSlab(RING.block.size_mm, slabMaterial())
    const b = new THREE.Box3().setFromObject(g)
    const s = b.getSize(new THREE.Vector3())
    expect([s.x, s.z, s.y].map((v) => +v.toFixed(3))).toEqual([RING.block.size_mm.x, RING.block.size_mm.y, RING.block.size_mm.z])
    expect(b.min.y).toBeCloseTo(0, 5)
  })
})

describe('view specs from records', () => {
  it('picked = model; not approved with a file = the model, marked in-design; no file = the slab', () => {
    const inDesign = { ...RING, exterior: { ...RING.exterior, status: 'not-picked' as const } }
    expect(exteriorView(inDesign)).toMatchObject({ slab: false, exterior: 'in-design' })
    expect(exteriorView(inDesign).model?.url).toContain('data/')
    expect(exteriorView(RING)).toMatchObject({ slab: false, exterior: 'picked' })
    const none = { ...RING, exterior: { ...RING.exterior, status: 'not-picked' as const, file: null } }
    expect(exteriorView(none)).toMatchObject({ slab: true, model: null, exterior: 'none' })
  })
  it('internals use the internals file of the record', () => {
    expect(internalsView(RING).model?.url).toContain('data/')
    expect(internalsView({ ...RING, internals: { ...RING.internals, file: null } }).model).toBeNull()
  })
})

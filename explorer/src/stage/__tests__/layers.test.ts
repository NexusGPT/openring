import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { EXPLODE_MIN_GAP_MM } from '../../contract/constants'
import { displacement, planLayers, toDesign, toThree } from '../layers'
import type { Part } from '../nodes'
import type { LayerRecord } from '../types'

const src = { file: 'x', line: 1 }
const layer = (id: string, order: number, explode?: LayerRecord['explode']): LayerRecord => ({ id, label: id, order, z_min: order, z_max: order + 1, source: src, explode })
const part = (name: string, layerId: string, at: [number, number, number]): Part => {
  const obj = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1))
  obj.position.set(...at)
  obj.updateMatrixWorld(true)
  return { name, obj, meshes: [obj], kind: 'plain', layer: layerId }
}

describe('explode by layer', () => {
  it('two touching layers end EXPLODE_MIN_GAP_MM apart when fully opened', () => {
    const plans = planLayers([layer('a', 0), layer('b', 1)], new Map([['a', [part('p', 'a', [0, 1, 0])]], ['b', [part('q', 'b', [0, 2, 0])]]]), -10)
    const c = new THREE.Vector3(0, 1, 0)
    const [pa, pb] = plans as [(typeof plans)[number], (typeof plans)[number]]
    const gap = displacement(pb, c, -10, 1).y - displacement(pa, c, -10, 1).y
    expect(gap).toBeCloseTo(EXPLODE_MIN_GAP_MM, 6)
  })
  it('assembled (0) moves nothing', () => {
    const plans = planLayers([layer('x', 0), layer('a', 3)], new Map(), -10)
    expect(displacement(plans[1] as (typeof plans)[number], new THREE.Vector3(), -10, 0).length()).toBe(0)
  })
  it("a layer's own direction (design coordinates) wins: design -z is three -y", () => {
    const plans = planLayers([layer('x', 0), layer('a', 1, { x: 0, y: 0, z: -1 })], new Map(), -10)
    const d = displacement(plans[1] as (typeof plans)[number], new THREE.Vector3(), -10, 1)
    expect(d.y).toBeLessThan(-1.9)
    expect(Math.abs(d.x) + Math.abs(d.z)).toBeLessThan(1e-9)
  })
  it('parts spread around the band move outward along their own radius', () => {
    const around = [0, 1, 2, 3].map((i) => part('r' + i, 'band', [0, -10 + 6 * Math.sin((i * Math.PI) / 2), 6 * Math.cos((i * Math.PI) / 2)]))
    const plans = planLayers([layer('x', 0), layer('band', 1)], new Map([['band', around]]), -10)
    const plan = plans[1] as (typeof plans)[number]
    expect(plan.dir).toBeNull()
    const below = displacement(plan, new THREE.Vector3(0, -16, 0), -10, 1)
    expect(below.y).toBeLessThan(-1.9)
    const side = displacement(plan, new THREE.Vector3(0, -10, 6), -10, 1)
    expect(side.z).toBeGreaterThan(1.9)
  })
  it('parts on one side of the band share one direction (up the stack)', () => {
    const plans = planLayers([layer('x', 0), layer('top', 1)], new Map([['top', [part('a', 'top', [0, 1, 0]), part('b', 'top', [3, 1, 2])]]]), -10)
    expect((plans[1] as (typeof plans)[number]).dir?.y).toBeGreaterThan(0.9)
  })
  it('design and three coordinates convert both ways', () => {
    const v = toThree({ x: 1, y: 2, z: 3 })
    expect(v.toArray()).toEqual([1, 3, -2])
    expect(toDesign(v)).toEqual([1, 2, 3])
  })
})

import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { EXPLODE_MIN_GAP_MM } from '../../contract/constants'
import { enclosureSet } from '../ghost'
import { displacement, planLayers, spreadIndex } from '../layers'
import type { Part } from '../nodes'
import type { LayerRecord } from '../types'

const part = (name: string, layer: string, at: [number, number, number], size: [number, number, number]): Part => {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size))
  mesh.position.set(...at)
  mesh.updateMatrixWorld(true)
  mesh.userData.restBox = new THREE.Box3().setFromObject(mesh)
  mesh.userData.restCentre = new THREE.Vector3(...at)
  return { name, obj: mesh, meshes: [mesh], kind: 'plain', layer }
}
const src = { file: 'x', line: 1 }

describe('enclosures ghost when open', () => {
  const skin = part('skin', 'body', [0, 0, 0], [20, 10, 10])
  const a = part('a', 'in', [-3, 0, 0], [2, 2, 2])
  const b = part('b', 'in', [3, 0, 0], [2, 2, 2])
  const far = part('far', 'out', [40, 0, 0], [2, 2, 2])
  it('a part whose box holds most other centres is an enclosure; the parts inside and outside are not', () => {
    expect([...enclosureSet([skin, a, b, far], new Map())]).toEqual(['skin'])
  })
  it('a part holding fewer than half of the others is not', () => {
    expect(enclosureSet([skin, a, far, part('far2', 'out', [60, 0, 0], [2, 2, 2])], new Map()).size).toBe(0)
  })
  it("the layer's ghost_when_open wins over the derivation, both ways", () => {
    expect([...enclosureSet([skin, a, b], new Map([['in', true]]))].sort()).toEqual(['a', 'b', 'skin'])
    expect(enclosureSet([skin, a, b], new Map([['body', false]])).size).toBe(0)
  })
})

describe('parts along one radius open one gap apart', () => {
  const axisY = 0
  // three parts on the ray at 90 degrees (straight up), one on the opposite side
  const parts = [part('liner', 'band', [0, 8, 0], [1, 1, 1]), part('cell', 'band', [0, 9.5, 0], [1, 1, 1]), part('shell', 'band', [0, 11, 0], [1, 1, 1]), part('other', 'band', [0, -9, 0], [1, 1, 1])]
  it('indexes them by distance from the axis; a part on another radius is not counted', () => {
    const s = spreadIndex(parts, axisY)
    expect([s.get('liner'), s.get('cell'), s.get('shell'), s.get('other')]).toEqual([0, 1, 2, 0])
  })
  it('the opened positions differ by one minimum gap along the radius', () => {
    const layers: LayerRecord[] = [{ id: 'band', label: 'b', order: 1, z_min: 0, z_max: 1, source: src, explode: 'radial' }]
    const plan = planLayers(layers, new Map([['band', parts]]), axisY)[0] as ReturnType<typeof planLayers>[number]
    const s = spreadIndex(parts, axisY)
    const at = (p: Part) => (p.obj.userData.restCentre as THREE.Vector3).clone().add(displacement(plan, p.obj.userData.restCentre, axisY, 1, s.get(p.name)))
    const [l, c, sh] = [at(parts[0] as Part), at(parts[1] as Part), at(parts[2] as Part)]
    expect(c.y - l.y).toBeCloseTo(1.5 + EXPLODE_MIN_GAP_MM, 6)
    expect(sh.y - c.y).toBeCloseTo(1.5 + EXPLODE_MIN_GAP_MM, 6)
  })
})

describe('opened gap is measured on the real boxes', () => {
  it('two layers that overlap 0.5 mm closed end at least EXPLODE_MIN_GAP_MM apart, neighbours that touch end exactly so', () => {
    const lower = part('lo', 'a', [0, 1, 0], [4, 2, 4]) // y 0..2
    const upper = part('up', 'b', [0, 2.5, 0], [4, 2, 4]) // y 1.5..3.5: overlaps by 0.5
    const top = part('top', 'c', [0, 4.5, 0], [4, 2, 4]) // y 3.5..5.5: touches
    const up = { x: 0, y: 0, z: 1 } // design +z = three +y
    const layers: LayerRecord[] = ['a', 'b', 'c'].map((id, i) => ({ id, label: id, order: i, z_min: 0, z_max: 1, source: src, explode: up }))
    const plans = planLayers(layers, new Map([['a', [lower]], ['b', [upper]], ['c', [top]]]), -10)
    const y = (pt: Part, i: number) => {
      const b = pt.obj.userData.restBox as THREE.Box3
      const d = displacement(plans[i] as (typeof plans)[number], pt.obj.userData.restCentre, -10, 1)
      return [b.min.y + d.y, b.max.y + d.y]
    }
    const [l, u, t] = [y(lower, 0), y(upper, 1), y(top, 2)] as [number[], number[], number[]]
    expect((u[0] as number) - (l[1] as number)).toBeGreaterThanOrEqual(EXPLODE_MIN_GAP_MM - 1e-9)
    expect((t[0] as number) - (u[1] as number)).toBeGreaterThanOrEqual(EXPLODE_MIN_GAP_MM - 1e-9)
    expect((t[0] as number) - (u[1] as number)).toBeCloseTo(EXPLODE_MIN_GAP_MM, 6)
  })
})

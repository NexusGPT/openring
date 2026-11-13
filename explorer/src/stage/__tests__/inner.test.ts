import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { classMaterials } from '../classMaterials'
import { Tween, smooth01 } from '../ease'
import { APPEAR_AT, InnerRing, type InnerState } from '../inner'
import type { LayerRecord, NodeSpec } from '../types'

const src = { file: 'x', line: 1 }
const layers: LayerRecord[] = [
  { id: 'body', label: 'b', order: 0, z_min: 0, z_max: 1, source: src, explode: { x: 0, y: 0, z: -1 } },
  { id: 'in', label: 'i', order: 1, z_min: 0, z_max: 1, source: src, explode: { x: 0, y: 0, z: 1 } },
]
const specs: NodeSpec[] = [
  { name: 'skin', kind: 'finish metal', layer: 'body' },
  { name: 'chipA', kind: 'plain', layer: 'in' },
  { name: 'cellB', kind: 'plain', layer: 'in' },
]
function model(): { root: THREE.Group; child: THREE.Mesh } {
  const root = new THREE.Group()
  const box = (w: number, h: number, d: number) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d))
  const skin = Object.assign(box(20, 10, 10), { name: 'skin' })
  const a = Object.assign(new THREE.Group(), { name: 'chipA' })
  const child = Object.assign(box(2, 2, 2), { name: 'chipA__chip' })
  child.position.set(-3, 0, 0)
  const unknown = Object.assign(box(1, 1, 1), { name: 'chipA__zzz' })
  unknown.position.set(-3, 3, 0)
  a.add(child, unknown)
  const b = Object.assign(box(2, 2, 2), { name: 'cellB' })
  b.position.set(3, 0, 0)
  root.add(skin, a, b)
  root.updateMatrixWorld(true)
  return { root, child }
}
const st = (p: Partial<InnerState> = {}): InnerState => ({ explode: 0, appear: smooth01(p.explode ?? 0, 0, APPEAR_AT), iso: 0, isolated: null, select: 0, selected: null, ...p })
const color = (m: THREE.Material) => (m as THREE.MeshStandardMaterial).color.getHexString()

describe('inside model transitions: end states', () => {
  it('closed: the inside is hidden in the exterior; at APPEAR_AT it is fully there, the enclosure a ghost', () => {
    const r = new InnerRing(model().root, specs, layers, -10, true)
    r.apply(st())
    expect(r.root.visible).toBe(false)
    r.apply(st({ explode: APPEAR_AT }))
    expect(r.root.visible).toBe(true)
    expect(r.parts.get('chipA')?.opacity).toBeCloseTo(1, 6)
    expect(r.parts.get('skin')?.opacity).toBeCloseTo(0.12, 6)
    expect(r.parts.get('skin')?.ghost).toBe(true)
  })
  it('isolating a layer fades the others to ghosts, it does not hide them', () => {
    const r = new InnerRing(model().root, specs, layers, -10, true)
    r.apply(st({ explode: 1, iso: 1, isolated: 'in' }))
    expect(r.parts.get('chipA')?.opacity).toBeCloseTo(1, 6)
    expect(r.parts.get('skin')?.opacity).toBeCloseTo(0.12, 6)
    expect(r.parts.get('skin')?.obj.visible).toBe(true)
    r.apply(st({ explode: 1, iso: 0.5, isolated: 'in' }))
    const mid = r.parts.get('cellB')?.opacity as number
    expect(mid).toBeGreaterThan(0.1)
    expect(mid).toBeLessThan(1.01)
  })
  it("isolating the enclosure's own layer makes it solid again", () => {
    const r = new InnerRing(model().root, specs, layers, -10, true)
    r.apply(st({ explode: 1, iso: 1, isolated: 'body' }))
    expect(r.parts.get('skin')?.opacity).toBeCloseTo(1, 6)
    expect(r.parts.get('skin')?.ghost).toBe(false)
  })
  it('a selected part gets an outline, others none', () => {
    const r = new InnerRing(model().root, specs, layers, -10, false)
    r.apply(st({ explode: 1, select: 1, selected: 'cellB' }))
    const lines = (n: string) => r.parts.get(n)?.meshes.flatMap((m) => m.children.filter((c) => (c as THREE.LineSegments).isLineSegments && c.visible)) ?? []
    expect(lines('cellB').length).toBeGreaterThan(0)
    expect(lines('chipA').length).toBe(0)
    r.apply(st({ explode: 1, select: 0, selected: null }))
    expect(lines('cellB').length).toBe(0)
  })
})

describe('materials by class', () => {
  it('a child <part>__<class> takes the class from the one table; picking it selects the top-level part', () => {
    const { root, child } = model()
    const r = new InnerRing(root, specs, layers, -10, false)
    expect(color(child.material as THREE.Material)).toBe(color(classMaterials.make('chip')))
    expect(r.partOf(child)).toBe('chipA')
  })
  it('an unknown class falls back to polymer and is reported', () => {
    const { root } = model()
    const r = new InnerRing(root, specs, layers, -10, false)
    const unknown = root.getObjectByName('chipA__zzz') as THREE.Mesh
    expect(color(unknown.material as THREE.Material)).toBe(color(classMaterials.make('polymer')))
    expect(r.unmapped).toContain('chipA__zzz')
  })
  it('without class children the part takes the class of its kind', () => {
    const { root } = model()
    new InnerRing(root, specs, layers, -10, false)
    expect(color((root.getObjectByName('skin') as THREE.Mesh).material as THREE.Material)).toBe(color(classMaterials.make('metal')))
  })
  it('the 15 classes all exist', () => {
    for (const c of ['metal', 'gold', 'pcb', 'chip', 'ceramic', 'polymer', 'glass', 'screen', 'foam', 'flex', 'cell', 'resin', 'mark', 'satin', 'soft'] as const) expect(classMaterials.has(c)).toBe(true)
  })
})

describe('nothing changes state in a single frame when motion is allowed', () => {
  it('explode, isolation and outline run through many frames; each frame moves a small share of the whole change', () => {
    const r = new InnerRing(model().root, specs, layers, -10, true)
    const explode = new Tween(0)
    const iso = new Tween(0)
    const select = new Tween(0)
    const appear = new Tween(0)
    explode.set(1, 0)
    appear.set(1, 0)
    iso.set(1, 0)
    select.set(1, 0)
    const track: Record<string, number[]> = { explode: [], skin: [], chipA: [], select: [] }
    for (let now = 0; now <= 340; now += 16) {
      explode.step(now)
      iso.step(now)
      select.step(now)
      appear.step(now)
      r.apply({ explode: explode.value, appear: appear.value, iso: iso.value, isolated: 'in', select: select.value, selected: 'cellB' })
      track.explode?.push(explode.value)
      track.skin?.push(r.parts.get('skin')?.opacity ?? 0)
      track.chipA?.push(r.parts.get('chipA')?.opacity ?? 0)
      track.select?.push(select.value)
    }
    for (const [name, v] of Object.entries(track)) {
      const total = Math.abs((v.at(-1) as number) - (v[0] as number))
      const worst = Math.max(...v.map((x, i) => (i ? Math.abs(x - (v[i - 1] as number)) : 0)))
      if (total > 0.2) expect(worst, name).toBeLessThan(total * 0.6)
      expect(new Set(v).size, name).toBeGreaterThan(4)
    }
  })
})

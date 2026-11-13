// screen-face-C16: with the glass on, nothing of the screen solid is drawn and the lit picture lies on the glass surface everywhere.
import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'
import { describe, expect, it } from 'vitest'
import type { RingModel } from '../../contract'
import { makeMaterials } from '../materials'
import { collectParts } from '../nodes'
import { buildFace, glassHeight, hideScreenUnderGlass } from '../viewExtras'

const DATA = resolve(__dirname, '../../../public/data')
const have = existsSync(`${DATA}/exterior.glb`) && existsSync(`${DATA}/ring-model.json`)

async function realParts() {
  const buf = readFileSync(`${DATA}/exterior.glb`)
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder)
  const gltf = await new Promise<{ scene: THREE.Object3D }>((ok, no) => loader.parse(Uint8Array.from(buf).buffer, '', ok, no))
  const root = new THREE.Group()
  root.add(gltf.scene)
  root.scale.setScalar(1000)
  root.updateMatrixWorld(true)
  const { parts } = collectParts(root, [{ name: 'glass', kind: 'glass' }, { name: 'screen', kind: 'screen' }])
  const ring = JSON.parse(readFileSync(`${DATA}/ring-model.json`, 'utf8')) as RingModel
  return { parts, ring }
}

describe('the lit picture on the real glass (screen-face-C16)', () => {
  it.skipIf(!have)('C16a with the glass on no face of the screen solid is drawn, and the picture plane exists', async () => {
    const { parts, ring } = await realParts()
    const mats = makeMaterials(new THREE.Texture())
    const face = buildFace(ring, parts, mats, new THREE.Scene())
    hideScreenUnderGlass(parts)
    expect(face?.material).toBe(mats.screenFace)
    const screen = parts.get('screen')
    expect(screen?.meshes.length).toBeGreaterThan(0)
    for (const m of screen?.meshes ?? []) expect(m.visible).toBe(false)
    for (const m of parts.get('glass')?.meshes ?? []) expect(m.visible).toBe(true)
  })
  it.skipIf(!have)('C16b the plane lies on or under the glass surface at its corners, edge midpoints, centre and every vertex', async () => {
    const { parts, ring } = await realParts()
    const mats = makeMaterials(new THREE.Texture())
    const face = buildFace(ring, parts, mats, new THREE.Scene()) as THREE.Mesh
    face.updateMatrixWorld(true)
    const glass = (parts.get('glass')?.meshes ?? []) as THREE.Mesh[]
    const { cx, cy, w, h } = ring.screens.rect
    const probes: [number, number][] = [[-1, -1], [1, -1], [1, 1], [-1, 1], [0, -1], [1, 0], [0, 1], [-1, 0], [0, 0]].map(([u, v]) => [cx + (u as number) * (w / 2), -cy + (v as number) * (h / 2)])
    for (const [x, z] of probes) {
      const g = glassHeight(glass, x, z)
      expect(g, `glass at ${x},${z}`).not.toBeNull()
      const p = new THREE.Vector3()
      let best = Infinity
      const pos = face.geometry.attributes.position as THREE.BufferAttribute
      for (let i = 0; i < pos.count; i++) {
        p.fromBufferAttribute(pos, i).applyMatrix4(face.matrixWorld)
        if (Math.hypot(p.x - x, p.z - z) < 1e-6) best = p.y
      }
      expect(best, `plane vertex at ${x},${z}`).toBeLessThanOrEqual((g as number) + 1e-6)
    }
    const pos = face.geometry.attributes.position as THREE.BufferAttribute
    const p = new THREE.Vector3()
    for (let i = 0; i < pos.count; i++) {
      p.fromBufferAttribute(pos, i).applyMatrix4(face.matrixWorld)
      expect(p.y).toBeLessThanOrEqual((glassHeight(glass, p.x, p.z) ?? Infinity) + 1e-6)
    }
    const b = new THREE.Box3().setFromObject(face)
    expect(b.max.x - b.min.x).toBeCloseTo(w, 6)
    expect(b.max.z - b.min.z).toBeCloseTo(h, 6)
  })
  it.skipIf(!have)('C16c the broken copy that leaves the slab visible is caught: the slab top is above the glass at its long edges', async () => {
    const { parts, ring } = await realParts()
    const glass = (parts.get('glass')?.meshes ?? []) as THREE.Mesh[]
    const top = new THREE.Box3().setFromObject(parts.get('screen')?.obj as THREE.Object3D).max.y
    const { cx, cy, h } = ring.screens.rect
    expect(top).toBeGreaterThan((glassHeight(glass, cx, -cy + h / 2 - 0.01) as number) + 0.05)
  })
})

describe('the same on a made-up dome (screen-face-C16d)', () => {
  it('C16d hideScreenUnderGlass hides the slab only when a glass is there', () => {
    const mk = (kind: 'glass' | 'screen') => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1))
      return { name: kind, obj: m, meshes: [m], kind, layer: null }
    }
    const withGlass = new Map([['glass', mk('glass')], ['screen', mk('screen')]])
    hideScreenUnderGlass(withGlass)
    expect(withGlass.get('screen')?.meshes[0]?.visible).toBe(false)
    expect(withGlass.get('glass')?.meshes[0]?.visible).toBe(true)
    const alone = new Map([['screen', mk('screen')]])
    hideScreenUnderGlass(alone)
    expect(alone.get('screen')?.meshes[0]?.visible).toBe(true)
  })
})

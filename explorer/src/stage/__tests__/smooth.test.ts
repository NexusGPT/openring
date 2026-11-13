import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { creaseNormals } from '../nodes'

// a 24-sided tube that arrives faceted: every triangle has its own normal
function faceted(): THREE.Mesh {
  const g = new THREE.CylinderGeometry(5, 5, 4, 24, 1, true).toNonIndexed()
  g.deleteAttribute('normal')
  g.computeVertexNormals()
  return new THREE.Mesh(g)
}

/** Largest angle (deg) between the normals that different triangles give the same position. */
function worstSeam(m: THREE.Mesh): number {
  const pos = m.geometry.attributes.position as THREE.BufferAttribute
  const nor = m.geometry.attributes.normal as THREE.BufferAttribute
  const at = new Map<string, THREE.Vector3[]>()
  for (let i = 0; i < pos.count; i++) {
    const k = [pos.getX(i), pos.getY(i), pos.getZ(i)].map((v) => v.toFixed(4)).join(',')
    at.set(k, [...(at.get(k) ?? []), new THREE.Vector3(nor.getX(i), nor.getY(i), nor.getZ(i))])
  }
  let worst = 0
  for (const ns of at.values()) for (const n of ns) worst = Math.max(worst, THREE.MathUtils.radToDeg(n.angleTo(ns[0] as THREE.Vector3)))
  return worst
}

describe('smooth normals for curved meshes that arrive faceted', () => {
  it('a faceted tube has seams; creasing removes them for the curve', () => {
    const m = faceted()
    expect(worstSeam(m)).toBeGreaterThan(10)
    creaseNormals(m, true)
    expect(worstSeam(m)).toBeLessThan(1)
  })
  it('a hard 90 degree edge stays sharp', () => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(2, 2, 2).toNonIndexed())
    creaseNormals(m, true)
    expect(worstSeam(m)).toBeGreaterThan(80)
  })
})

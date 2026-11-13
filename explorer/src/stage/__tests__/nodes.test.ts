import * as THREE from 'three'
import { describe, expect, it } from 'vitest'
import { baseName, collectParts } from '../nodes'

const mesh = (name: string) => Object.assign(new THREE.Mesh(), { name })
const specs = [
  { name: 'alpha', kind: 'glass' as const, layer: 'l1' },
  { name: 'beta_1', kind: 'gold' as const },
]

describe('parts from the node-to-kind map', () => {
  it('finds a part by the mesh name, by a numbered primitive and by a parent group', () => {
    const root = new THREE.Group()
    const g = Object.assign(new THREE.Group(), { name: 'alpha' })
    g.add(mesh('alpha_1'), mesh('alpha_2'))
    root.add(g, mesh('beta_1'))
    const { parts, unmapped } = collectParts(root, specs)
    expect([...parts.keys()].sort()).toEqual(['alpha', 'beta_1'])
    expect(parts.get('alpha')?.meshes).toHaveLength(2)
    expect(parts.get('alpha')?.layer).toBe('l1')
    expect(unmapped).toEqual([])
  })
  it('a part with several primitives under a group of its own name moves as the group', () => {
    const root = new THREE.Group()
    const g = Object.assign(new THREE.Group(), { name: 'alpha' })
    g.add(mesh('alpha_1'), mesh('alpha_2'))
    root.add(g)
    expect(collectParts(root, specs).parts.get('alpha')?.obj).toBe(g)
  })
  it('a node that is not in the map is reported, once, by its own name', () => {
    const root = new THREE.Group()
    root.add(mesh('gamma'), mesh('gamma'))
    const { unmapped } = collectParts(root, specs)
    expect(unmapped).toEqual(['gamma'])
  })
  it('an unmapped group is reported by the group name, not by its numbered primitives or its container', () => {
    const root = new THREE.Group()
    const scene = Object.assign(new THREE.Group(), { name: 'container' })
    const g = Object.assign(new THREE.Group(), { name: 'delta' })
    g.add(mesh('delta_1'), mesh('delta_2'))
    scene.add(g)
    root.add(scene)
    expect(collectParts(root, specs).unmapped).toEqual(['delta'])
  })
  it('strips loader suffixes only as a fallback', () => {
    expect(baseName('x.001')).toBe('x')
    expect(baseName('x_12')).toBe('x')
    expect(baseName('plain')).toBe('plain')
  })
})

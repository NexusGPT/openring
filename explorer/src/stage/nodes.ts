// Turns a loaded model into named PARTS. A part is the nearest ancestor-or-self of a mesh whose
// name is in the bundle's node-to-kind map. A mesh with no such ancestor is UNMAPPED: it is
// drawn with the plain material and reported by unmappedNodes().
import * as THREE from 'three'
import { toCreasedNormals } from 'three/addons/utils/BufferGeometryUtils.js'
import type { Kind } from '../contract'
import type { NodeSpec } from './types'

export interface Part {
  name: string
  obj: THREE.Object3D
  meshes: THREE.Mesh[]
  kind: Kind
  layer: string | null
  /** drawn as a ghost now (an enclosure while the ring is open); picks pass through it */
  ghost?: boolean
  /** opacity now, 0..1 (inside parts) */
  opacity?: number
  /** material class per mesh, from a child named <part>__<class>; absent = the class of the part's kind */
  classes?: Map<THREE.Mesh, string>
}

export interface ModelParts {
  parts: Map<string, Part>
  unmapped: string[]
}

/** glTF loaders add a numeric suffix to repeated names: 'name.001', 'name_1'. */
export function baseName(name: string): string {
  return name.replace(/[._ -]?\d{1,3}$/, '')
}

function matchName(name: string, known: ReadonlyMap<string, NodeSpec>): string | null {
  if (known.has(name)) return name
  const b = baseName(name)
  return known.has(b) ? b : null
}

/** Name used to report an unmapped mesh: the group its numbered primitives hang under, else its own name. */
function reportName(mesh: THREE.Object3D, root: THREE.Object3D): string {
  let name = mesh.name
  for (let o = mesh.parent; o && o !== root && o.name && (o.name === name || o.name === baseName(name)); o = o.parent) name = o.name
  return name || '(unnamed)'
}

/** Class named by the node between a mesh and its part: `<part>__<class>` (numeric suffixes ignored). */
export function classBelow(mesh: THREE.Object3D, part: THREE.Object3D): string | null {
  for (let o: THREE.Object3D | null = mesh; o && o !== part.parent; o = o.parent) {
    const m = /__([A-Za-z]+)(?:[._ -]?\d{1,3})?$/.exec(o.name)
    if (m?.[1]) return m[1].toLowerCase()
  }
  return null
}

export function collectParts(root: THREE.Object3D, specs: readonly NodeSpec[]): ModelParts {
  const known = new Map(specs.map((s) => [s.name, s]))
  const parts = new Map<string, Part>()
  const unmapped = new Set<string>()
  root.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) return
    for (let p: THREE.Object3D | null = mesh; p && p !== root; p = p.parent) {
      const hit = matchName(p.name, known)
      if (!hit) continue
      const spec = known.get(hit) as NodeSpec
      // a part whose primitives hang under a group of the same name moves as the group, not as its first primitive
      let top: THREE.Object3D = p
      while (top.parent && top.parent !== root && matchName(top.parent.name, known) === hit) top = top.parent
      let part = parts.get(hit)
      if (!part) {
        part = { name: hit, obj: top, meshes: [], kind: spec.kind, layer: spec.layer ?? null, classes: new Map() }
        parts.set(hit, part)
      }
      part.meshes.push(mesh)
      const cls = classBelow(mesh, p)
      if (cls) (part.classes ??= new Map()).set(mesh, cls)
      return
    }
    unmapped.add(reportName(mesh, root))
  })
  return { parts, unmapped: [...unmapped] }
}

const smoothed = new WeakMap<THREE.BufferGeometry, THREE.BufferGeometry>()

/** Smooth the normals of a curved mesh that arrives faceted (corners under 34 degrees are blended, sharper stay sharp). */
export function creaseNormals(mesh: THREE.Mesh, force = false): void {
  const g = mesh.geometry
  if (g.userData.creased) return
  if (g.attributes.normal && !force) return
  let out = smoothed.get(g)
  if (!out) {
    out = toCreasedNormals(g, 0.6)
    out.userData.creased = true
    smoothed.set(g, out)
  }
  mesh.geometry = out
}

/** Part name of a clicked mesh, or null. */
export function partOfMesh(mesh: THREE.Object3D, parts: ReadonlyMap<string, Part>): string | null {
  for (const [name, part] of parts) if (part.meshes.includes(mesh as THREE.Mesh)) return name
  return null
}

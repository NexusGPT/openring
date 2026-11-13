// The inside model of the ring: parts with their own materials (one table, classMaterials.ts), explode by
// layer, and the soft transitions: parts appear as the ring opens, enclosures and non-isolated layers fade
// to ghosts (never switch off), and a selected part gets an outline. Everything is a function of one state
// (explode, isolation, selection) so a frame in between is simply an in-between state.
import * as THREE from 'three'
import { GHOST_OPACITY, coveringShells, enclosureSet, isThinShell } from './ghost'
import { KIND_CLASS, classMaterials } from './classMaterials'
import { displacement, placeOffset, planLayers, spreadIndex, type LayerPlan } from './layers'
import { collectParts, creaseNormals, type Part } from './nodes'
import { restBox } from './ghost'
import { cssColour } from './tokens'
import type { LayerRecord, NodeSpec } from './types'

/** Explode value at which the inside has fully appeared and the enclosures are fully ghosts. */
export const APPEAR_AT = 0.25

export interface InnerState {
  explode: number
  /** 0..1 cross-fade of exterior -> inside (smooth01 of the control, eased in time like everything else) */
  appear: number
  /** 0..1 how far the isolation fade has run, and which layer is isolated (kept while it fades back) */
  iso: number
  isolated: string | null
  /** 0..1 outline strength of the selected node */
  select: number
  selected: string | null
}

export class InnerRing {
  readonly parts: Map<string, Part>
  readonly unmapped: string[]
  readonly plans: LayerPlan[]
  private meshPart = new Map<THREE.Object3D, Part>()
  private partMats = new Map<Part, THREE.Material[]>()
  private enclosures: Set<string>
  private partFlags: Map<string, boolean>
  /** thin shells (candidates) and, per frame, how far each has faded as a cover: name -> 0..1 */
  private thin = new Set<string>()
  private cover = new Map<string, number>()
  private covering = new Set<string>()
  private spread = new Map<string, number>()
  private lines = new Map<THREE.Mesh, { ghost?: THREE.LineSegments; outline?: THREE.LineSegments }>()
  private ghostMat: THREE.LineBasicMaterial
  private outlineMat: THREE.LineBasicMaterial

  constructor(readonly root: THREE.Object3D, specs: readonly NodeSpec[], layers: readonly LayerRecord[], readonly axisY: number, private fade: boolean, partFlags: ReadonlyMap<string, boolean> = new Map()) {
    this.partFlags = new Map(partFlags)
    const found = collectParts(root, specs)
    this.parts = found.parts
    this.unmapped = [...found.unmapped]
    const plain = classMaterials.make('polymer')
    root.traverse((o) => {
      const mesh = o as THREE.Mesh
      if (!mesh.isMesh) return
      creaseNormals(mesh, true)
      mesh.material = plain // not in the map: polymer, listed by unmappedNodes()
    })
    for (const p of this.parts.values()) {
      const made = new Map<string, THREE.Material>()
      for (const m of p.meshes) {
        const named = p.classes?.get(m)
        const cls = named && classMaterials.has(named) ? named : named ? 'polymer' : KIND_CLASS[p.kind]
        if (named && !classMaterials.has(named)) this.unmapped.push(`${p.name}__${named}`)
        if (!made.has(cls)) made.set(cls, classMaterials.make(cls as never))
        m.material = made.get(cls) as THREE.Material
        this.meshPart.set(m, p)
      }
      this.partMats.set(p, [...made.values()])
      const rb = new THREE.Box3().setFromObject(p.obj)
      p.obj.userData.restBox = rb
      p.obj.userData.restCentre = rb.getCenter(new THREE.Vector3())
    }
    const all = [...this.parts.values()]
    const flags = new Map(layers.map((l) => [l.id, l.ghost_when_open ?? undefined]))
    this.enclosures = enclosureSet(all, flags, this.partFlags)
    for (const p of all) if (this.partFlags.get(p.name) !== false && !this.enclosures.has(p.name) && isThinShell(p)) this.thin.add(p.name)
    const byLayer = new Map<string, Part[]>()
    for (const p of all) if (p.layer) byLayer.set(p.layer, [...(byLayer.get(p.layer) ?? []), p])
    this.plans = planLayers(layers, byLayer, axisY)
    for (const l of layers) if (l.explode === 'radial') for (const [n, i] of spreadIndex(byLayer.get(l.id) ?? [], axisY)) this.spread.set(n, i)
    this.ghostMat = new THREE.LineBasicMaterial({ color: cssColour('--hairline', '#e7e8ea'), transparent: true, opacity: 0 })
    this.outlineMat = new THREE.LineBasicMaterial({ color: cssColour('--ink', '#111214'), transparent: true, opacity: 0, depthTest: false })
  }

  /** Union of the parts' boxes with the layers opened by `explode` (for fitting the camera). */
  boxAt(explode: number): THREE.Box3 {
    const out = new THREE.Box3()
    const byId = new Map(this.plans.map((p) => [p.id, p]))
    for (const p of this.parts.values()) {
      const plan = p.layer ? byId.get(p.layer) : undefined
      const d = plan ? displacement(plan, p.obj.userData.restCentre as THREE.Vector3, this.axisY, explode, this.spread.get(p.name) ?? 0) : new THREE.Vector3()
      out.union(restBox(p).clone().translate(d))
    }
    return out
  }

  partOf(mesh: THREE.Object3D): string | null {
    return this.meshPart.get(mesh)?.name ?? null
  }

  private line(mesh: THREE.Mesh, kind: 'ghost' | 'outline'): THREE.LineSegments {
    const entry = this.lines.get(mesh) ?? {}
    this.lines.set(mesh, entry)
    let l = entry[kind]
    if (!l) {
      l = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry, 30), kind === 'ghost' ? this.ghostMat : this.outlineMat)
      l.renderOrder = kind === 'outline' ? 6 : 1
      entry[kind] = l
      mesh.add(l)
    }
    return l
  }

  /** Which thin shells cover another part from this camera (call now and then while the ring is open). */
  updateCover(camera: THREE.Camera): void {
    const all = [...this.parts.values()]
    const shells = all.filter((p) => this.thin.has(p.name))
    this.covering = coveringShells(camera, shells, all.filter((p) => !this.enclosures.has(p.name)))
  }

  apply(s: InnerState): void {
    const e = s.explode
    const a = this.fade ? s.appear : 1
    this.root.visible = a > 0.001
    const byId = new Map(this.plans.map((p) => [p.id, p]))
    let ghostEdge = 0
    for (const p of this.parts.values()) {
      const plan = p.layer ? byId.get(p.layer) : undefined
      if (plan) placeOffset(p.obj, displacement(plan, p.obj.userData.restCentre as THREE.Vector3, this.axisY, e, this.spread.get(p.name) ?? 0))
      const cl = this.cover.get(p.name) ?? 0
      const toward = this.covering.has(p.name) ? 1 : 0
      this.cover.set(p.name, cl + (toward - cl) * 0.25) // a shell that starts to cover fades in over a few frames
      let gE = this.enclosures.has(p.name) ? s.appear : this.thin.has(p.name) ? s.appear * (this.cover.get(p.name) as number) : 0
      if (s.isolated !== null && p.layer === s.isolated) gE *= 1 - s.iso
      const gI = s.isolated !== null && p.layer !== s.isolated ? s.iso : 0
      const ghost = Math.max(gE, gI)
      const opacity = a * (1 - (1 - GHOST_OPACITY) * ghost)
      p.opacity = opacity
      p.ghost = ghost > 0.5
      for (const m of this.partMats.get(p) ?? []) {
        m.transparent = opacity < 0.999
        m.opacity = opacity
        m.depthWrite = opacity > 0.98
      }
      if (ghost > 0.001) {
        ghostEdge = Math.max(ghostEdge, ghost * a)
        for (const m of p.meshes) this.line(m, 'ghost').visible = true
      } else for (const m of p.meshes) if (this.lines.get(m)?.ghost) (this.lines.get(m)?.ghost as THREE.LineSegments).visible = false
      const sel = s.selected === p.name && s.select > 0.001
      for (const m of p.meshes) {
        if (sel) this.line(m, 'outline').visible = true
        else if (this.lines.get(m)?.outline) (this.lines.get(m)?.outline as THREE.LineSegments).visible = false
      }
    }
    this.ghostMat.opacity = ghostEdge
    this.outlineMat.opacity = 0.9 * s.select
  }
}

// One view of the stage: its own scene, camera and orbit controls over one DOM region of the shared canvas.
// The content is built from the loaded models plus the bundle records; nothing here names a part.
//   exterior (+ inner): the ring as on Home; the inside model hides in it and appears as the ring opens
//   internals alone: the inside model (harness, tests)         case: the case with its lid
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import type { PartPlacements, RingModel } from '../contract'
import { classMaterials } from './classMaterials'
import { bezier, motionTokens } from './ease'
import { InnerRing, type InnerState } from './inner'
import { rotateAbout } from './lid'
import type { KindMaterials } from './materials'
import { collectParts, creaseNormals, type Part } from './nodes'
import { fadeShell, forkShell, type Shell } from './shell'
import { makeSlab, slabMaterial } from './slab'
import type { LayerRecord, StageProps, ViewPreset, ViewSpec } from './types'
import { fitDistance, poseCamera, presetPose, type Framing } from './viewPresets'
import { FINGER_GAP_MM, SHADOW_D, SHADOW_W, buildFace, buildFinger, buildGlow, buildShadows, hideScreenUnderGlass } from './viewExtras'

/** `ghost_when_open` per part, from the placements record when it carries it (keyed by the node name). */
function partFlagsOf(pl: PartPlacements | null): Map<string, boolean> {
  const m = new Map<string, boolean>()
  for (const p of (pl?.placements ?? []) as Array<{ name: string; ghost_when_open?: boolean | null }>) if (typeof p.ghost_when_open === 'boolean') m.set(p.name, p.ghost_when_open)
  return m
}

export type LoadState = 'loading' | 'ok' | 'failed'
interface CamMove { t0: number; ms: number; curve: readonly [number, number, number, number]; fromP: THREE.Vector3; fromT: THREE.Vector3; toP: THREE.Vector3; toT: THREE.Vector3 }

export class StageView {
  readonly scene = new THREE.Scene()
  readonly camera = new THREE.PerspectiveCamera(28, 1, 1, 2000)
  readonly controls: OrbitControls
  state: LoadState = 'loading'
  unmapped: string[] = []
  framing: Framing | null = null
  inner: InnerRing | null = null
  shell: Shell | null = null
  finger: THREE.Mesh | null = null
  glow: THREE.Sprite | null = null
  face: THREE.Mesh | null = null
  touched = false
  lastPreset: ViewPreset = 'three-quarter'
  anim: CamMove | null = null
  lidNow = 0
  /** opacity of the exterior shell now (1 closed .. 0 open) */
  shellOpacity = 1
  private shellParts = new Map<string, Part>()
  private meshPart = new Map<THREE.Object3D, Part>()
  private shadows: THREE.Mesh[] = []
  private cue: THREE.Group | null = null
  private lidRest: THREE.Matrix4 | null = null
  private highlighted: Part | null = null
  private closedFit = new THREE.Box3()
  private fitR = 0
  private framed: string | null = null
  private coverT = 0

  constructor(public spec: ViewSpec, readonly el: HTMLElement, env: THREE.Texture, private mats: KindMaterials, autoRotate: boolean) {
    this.scene.environment = env
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0xb8a090, 1.6))
    this.controls = new OrbitControls(this.camera, el)
    Object.assign(this.controls, { enableDamping: true, dampingFactor: 0.08, enablePan: false, minDistance: 8, maxDistance: 400, autoRotate, autoRotateSpeed: 1.6 })
  }

  fail = (): void => void (this.state = 'failed')

  /** The parts that can be clicked and exploded: the inside model's when there is one. */
  get parts(): Map<string, Part> {
    return this.inner?.parts ?? this.shellParts
  }

  /** Put the loaded model(s) in the scene and build everything around them. */
  build(model: THREE.Object3D | null, innerModel: THREE.Object3D | null, ring: RingModel | null, placements: PartPlacements | null): void {
    const spec = this.spec
    const layers = (placements?.layers ?? []) as LayerRecord[]
    const root = spec.slab && ring ? makeSlab(ring.block.size_mm, slabMaterial()) : model
    if (!root) return this.fail()
    this.scene.add(root)
    root.updateMatrixWorld(true)
    const whole = new THREE.Box3().setFromObject(root)
    const f = this.framingOf(whole, ring)
    if (spec.role === 'internals') {
      this.inner = new InnerRing(root, spec.nodes, layers, f.axisY, false, partFlagsOf(placements))
    } else {
      if (!spec.slab) this.buildShell(root, ring)
      if (spec.inner && innerModel) {
        this.scene.add(innerModel)
        innerModel.updateMatrixWorld(true)
        this.inner = new InnerRing(innerModel, spec.inner.nodes, layers, f.axisY, true, partFlagsOf(placements))
        this.shell = forkShell(root)
      }
    }
    this.unmapped = [...this.shellUnmapped, ...(this.inner?.unmapped ?? [])]
    this.closedFit = f.fit.clone()
    if (spec.role === 'exterior' && !spec.slab) {
      this.face = buildFace(ring, this.shellParts, this.mats, this.scene)
      hideScreenUnderGlass(this.shellParts)
      this.glow = buildGlow(this.shellParts, this.scene)
      this.mats.screenFace.opacity = 1
    }
    this.shadows = buildShadows(whole, f.block, this.scene)
    const fg = spec.role === 'exterior' ? buildFinger(f.block, f.axisY, f.innerD, this.scene) : null
    this.finger = fg?.finger ?? null
    this.cue = fg?.cue ?? null
    this.state = 'ok'
    this.setPreset('three-quarter', true)
    this.fitR = presetPose(f, 'three-quarter').r
  }

  private shellUnmapped: string[] = []

  private buildShell(root: THREE.Object3D, ring: RingModel | null): void {
    void ring
    const found = collectParts(root, this.spec.nodes)
    this.shellParts = found.parts
    this.shellUnmapped = found.unmapped
    root.traverse((o) => {
      const mesh = o as THREE.Mesh
      if (!mesh.isMesh) return
      creaseNormals(mesh)
      // not in the map: an exterior is one finish, so it takes the finish; listed by unmappedNodes()
      mesh.material = this.spec.role === 'exterior' ? this.mats.byKind['finish metal'] : this.mats.byKind.plain
    })
    const caseMats = new Map<string, THREE.Material>()
    const specOf = new Map(this.spec.nodes.map((n) => [n.name, n]))
    for (const p of this.shellParts.values()) {
      for (const m of p.meshes) {
        const cls = this.spec.role === 'case' ? specOf.get(p.name)?.materialClass : undefined
        if (cls && classMaterials.has(cls)) {
          if (!caseMats.has(cls)) caseMats.set(cls, classMaterials.make(cls))
          m.material = caseMats.get(cls) as THREE.Material
        } else m.material = this.mats.byKind[p.kind]
        this.meshPart.set(m, p)
      }
      const rb = new THREE.Box3().setFromObject(p.obj)
      p.obj.userData.restBox = rb
      p.obj.userData.restCentre = rb.getCenter(new THREE.Vector3())
    }
  }

  private framingOf(whole: THREE.Box3, ring: RingModel | null): Framing {
    const innerD = ring?.band.inner_diameter_mm ?? 0
    const thick = ring?.block.size_mm.z ?? whole.max.y - whole.min.y
    const bw = ring?.block.size_mm.x ?? whole.max.x - whole.min.x
    const bd = ring?.block.size_mm.y ?? whole.max.z - whole.min.z
    const cx = (whole.min.x + whole.max.x) / 2
    const block = new THREE.Box3(new THREE.Vector3(cx - bw / 2, whole.max.y - thick, -bd / 2), new THREE.Vector3(cx + bw / 2, whole.max.y, bd / 2))
    const wallR = (whole.max.z - whole.min.z) / 2
    // coaxial with the band: outer radius from the lateral size, else the block underside minus a gap
    const axisY = innerD > 0 && wallR > innerD / 2 + 0.05 ? whole.min.y + wallR : block.min.y - FINGER_GAP_MM - innerD / 2
    const sx = bw * SHADOW_W
    const shadow = new THREE.Box3(new THREE.Vector3(cx - sx / 2, whole.min.y - 0.05, (-sx * SHADOW_D) / 2), new THREE.Vector3(cx + sx / 2, whole.min.y, (sx * SHADOW_D) / 2))
    return (this.framing = { whole, block, axisY, innerD, fit: whole.clone().union(shadow) })
  }

  setPreset(name: ViewPreset, instant: boolean): void {
    if (!this.framing) return
    const { pos, target } = poseCamera(this.camera, presetPose(this.framing, name))
    const onFinger = name === 'finger'
    if (this.finger) this.finger.visible = onFinger
    if (this.cue) this.cue.visible = onFinger
    for (const s of this.shadows) s.visible = !onFinger
    this.moveCamera(pos, target, instant)
  }

  private moveCamera(pos: THREE.Vector3, target: THREE.Vector3, instant: boolean): void {
    const m = motionTokens()
    if (instant || m.ms <= 0) {
      this.camera.position.copy(pos)
      this.controls.target.copy(target)
      this.controls.update()
      this.anim = null
    } else {
      this.anim = { t0: performance.now(), ms: m.ms, curve: m.curve, fromP: this.camera.position.clone(), fromT: this.controls.target.clone(), toP: pos, toT: target }
    }
  }

  /** Advance the eased camera move to time `now` (ms); true while it runs. */
  stepAnim(now: number): boolean {
    const a = this.anim
    if (!a) return false
    const p = Math.min(1, Math.max(0, (now - a.t0) / a.ms))
    const e = bezier(a.curve, p)
    this.camera.position.lerpVectors(a.fromP, a.toP, e)
    this.controls.target.lerpVectors(a.fromT, a.toT, e)
    if (p >= 1) this.anim = null
    return true
  }

  resize(w: number, h: number): void {
    if (w < 1 || h < 1) return
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
    if (!this.framing || this.anim) return
    const sel = this.framed ? this.parts.get(this.framed) : undefined
    if (sel) {
      // a part is framed: keep it framed at the new size (turning the ring keeps the direction and the target)
      const pose = this.selectionPose(sel)
      const dir = this.camera.position.clone().sub(this.controls.target).normalize()
      const keep = this.touched ? this.controls.target.clone() : pose.target
      return this.moveCamera(keep.clone().add(dir.multiplyScalar(pose.pos.distanceTo(pose.target))), keep, true)
    }
    if (!this.touched) return this.setPreset(this.lastPreset, true)
    // the owner turned the ring: keep the direction, refit the distance to the new size
    const pose = presetPose(this.framing, this.lastPreset)
    const dir = this.camera.position.clone().sub(this.controls.target).normalize()
    this.camera.position.copy(this.controls.target).add(dir.multiplyScalar(fitDistance(this.camera, pose.r)))
  }

  /** One frame of the opening/isolation/selection state. */
  applyMotion(s: InnerState): void {
    if (!this.inner) return
    const e = s.explode
    if (s.explode > 0.25 && performance.now() - this.coverT > 250) {
      this.coverT = performance.now()
      this.camera.updateMatrixWorld(true)
      this.inner.updateCover(this.camera)
    }
    this.inner.apply(s)
    if (this.shell) {
      this.shellOpacity = 1 - s.appear
      fadeShell(this.shell, this.shellOpacity)
      this.mats.screenFace.opacity = this.shellOpacity
      if (this.face) this.face.visible = this.shellOpacity > 0.01
    } else this.shellOpacity = 1
    this.refit(this.inner.boxAt(e))
  }

  /** The whole view (closed ring plus whatever has opened: layers, lid) stays inside the margin: grow or shrink the distance. */
  private refit(open: THREE.Box3): void {
    if (!this.framing) return
    this.framing.fit = this.closedFit.clone().union(open)
    const r = presetPose(this.framing, this.lastPreset).r
    if (this.fitR > 0 && r !== this.fitR && !this.anim) {
      const off = this.camera.position.clone().sub(this.controls.target)
      this.camera.position.copy(this.controls.target).add(off.multiplyScalar(r / this.fitR))
    }
    this.fitR = r
  }

  /** Draw each state the transitions use once, tiny, so the first opening does not stall on shader compilation or uploads. */
  warm(r: THREE.WebGLRenderer): void {
    if (!this.inner) return
    const base: InnerState = { explode: 1, appear: 1, iso: 0, isolated: null, select: 0, selected: null }
    const first = [...this.parts.values()].find((p) => p.layer)?.layer ?? null
    for (const st of [{ ...base, iso: 1, isolated: first, select: 1, selected: [...this.parts.keys()][0] ?? null }, { ...base, appear: 0.5 }, base]) {
      this.applyMotion(st)
      r.setScissorTest(false)
      r.setViewport(0, 0, 2, 2)
      r.render(this.scene, this.camera) // a real (tiny) draw: shaders compiled and geometry uploaded before the first opening
    }
  }

  applyProps(p: StageProps): void {
    if (this.glow) this.glow.visible = !!p.lightOn && this.shellOpacity > 0.01
    this.frameSelection(p.selectedNode ?? null)
  }

  /** Select: ease the camera to frame the part; deselect: ease back to the preset. Never a cut. */
  private frameSelection(node: string | null): void {
    if (node === this.framed || this.state !== 'ok') return
    this.framed = node
    if (this.highlighted) for (const m of this.highlighted.meshes) m.material = this.mats.byKind[this.highlighted.kind]
    this.highlighted = null
    const part = node ? this.parts.get(node) : undefined
    if (!this.inner && part) {
      this.highlighted = part
      for (const m of part.meshes) m.material = this.mats.highlight[part.kind]
      return
    }
    if (!part) return this.setPreset(this.lastPreset, false)
    const pose = this.selectionPose(part)
    this.moveCamera(pose.pos, pose.target, false)
  }

  /** Close on the part, never farther than the whole ring; the viewing direction is kept. */
  private selectionPose(part: Part): { pos: THREE.Vector3; target: THREE.Vector3 } {
    const box = new THREE.Box3().setFromObject(part.obj)
    const target = box.getCenter(new THREE.Vector3())
    const wholeR = this.framing ? presetPose(this.framing, this.lastPreset).r : Infinity
    const r = Math.min(Math.max(box.getBoundingSphere(new THREE.Sphere()).radius * 1.1, 4), wholeR)
    const dir = this.camera.position.clone().sub(this.controls.target).normalize()
    return { pos: target.clone().add(dir.multiplyScalar(fitDistance(this.camera, r))), target }
  }

  /** Part name of a mesh of this view, or null. */
  partOf(mesh: THREE.Object3D): string | null {
    return this.inner?.partOf(mesh) ?? this.meshPart.get(mesh)?.name ?? null
  }

  applyLid(deg: number): void {
    const lid = this.spec.lid
    const p = lid ? this.shellParts.get(lid.node) : undefined
    if (!lid || !p) return
    this.lidRest = rotateAbout(p.obj, this.lidRest, lid.point, lid.axis, deg)
    this.lidNow = deg
    this.refit(new THREE.Box3().setFromObject(p.obj)) // the open lid stays in frame
  }

  dispose(): void {
    this.controls.dispose()
    this.scene.clear()
  }
}

// window.__stage, typed in src/contract/stage-api.ts. Checks and journeys read only these members.
import * as THREE from 'three'
import type { StageApi } from '../contract'
import { toDesign } from './layers'
import { materialHex } from './materials'
import { contextCount, type StageEngine } from './engine'
import { surfacePoint } from './surface'
import { fieldLabels, findState } from './screenFace'

export function installTestApi(e: StageEngine): StageApi {
  const first = () => [...e.views.values()].find((v) => v.state === 'ok')
  const api: StageApi = {
    get ready() {
      return e.ready
    },
    get contexts() {
      return contextCount
    },
    get frames() {
      return e.frames
    },
    get autoRotate() {
      return e.autoRotate
    },
    azimuthDeg: () => THREE.MathUtils.radToDeg(first()?.controls.getAzimuthalAngle() ?? 0),
    unmappedNodes: () => [...new Set([...e.views.values()].flatMap((v) => v.unmapped))],
    layerBoxes() {
      const out: ReturnType<StageApi['layerBoxes']> = {}
      for (const v of e.views.values()) {
        for (const l of e.props?.placements?.layers ?? []) {
          const b = new THREE.Box3()
          for (const p of v.parts.values()) if (p.layer === l.id) b.expandByObject(p.obj)
          if (b.isEmpty()) continue
          const lo = toDesign(b.min)
          const hi = toDesign(b.max)
          out[l.id] = { min: [Math.min(lo[0], hi[0]), Math.min(lo[1], hi[1]), Math.min(lo[2], hi[2])], max: [Math.max(lo[0], hi[0]), Math.max(lo[1], hi[1]), Math.max(lo[2], hi[2])] }
        }
      }
      return out
    },
    screenPos(n) {
      for (const [id, v] of e.views) {
        const p = v.parts.get(n)
        const b = e.rects.get(id)
        if (!p || !b || v.state !== 'ok') continue
        const c = surfacePoint(v.camera, v.parts, p) // a point ON the part, not the centre of its box
        if (!c) continue
        return { x: b.x + ((c.x + 1) / 2) * b.w, y: (e.host?.getBoundingClientRect().height ?? 0) - b.y - b.h + ((1 - c.y) / 2) * b.h }
      }
      return null
    },
    isolatedLayer: () => e.props?.isolatedLayer ?? null,
    material(option, node) {
      const part = e.views.get(option)?.parts.get(node)
      const hex = materialHex(part?.meshes[0]?.material)
      return hex ? { color: hex } : null
    },
    fingerVisible: (option) => !!e.views.get(option)?.finger?.visible,
    lightOn: () => !!e.props?.lightOn,
    screenFields: () => fieldLabels(findState(e.props?.ringModel ?? null, e.props?.screenState)),
    nodeRotationDeg(node) {
      for (const v of e.views.values()) if (v.spec.lid?.node === node) return v.lidNow
      return 0
    },
    clearColor() {
      const c = new THREE.Color()
      e.renderer?.getClearColor(c)
      return { colour: `#${c.getHexString()}`, alpha: e.renderer?.getClearAlpha() ?? 0 }
    },
    fitBox(option) {
      const v = e.views.get(option)
      if (!v?.framing || v.state !== 'ok') return null
      const b = v.framing.fit
      let l = 1, r = 0, t = 1, bo = 0
      for (const x of [b.min.x, b.max.x]) for (const y of [b.min.y, b.max.y]) for (const z of [b.min.z, b.max.z]) {
        const p = new THREE.Vector3(x, y, z).project(v.camera)
        l = Math.min(l, (p.x + 1) / 2); r = Math.max(r, (p.x + 1) / 2); t = Math.min(t, (1 - p.y) / 2); bo = Math.max(bo, (1 - p.y) / 2)
      }
      return { left: l, right: r, top: t, bottom: bo }
    },
    exteriorState: () => e.props?.views.find((v) => v.role === 'exterior')?.exterior ?? null,
    exteriorOpacity: () => [...e.views.values()].find((v) => v.shell)?.shellOpacity ?? null,
    partOpacity: (n) => [...e.views.values()].map((v) => v.parts.get(n)?.opacity).find((o) => o !== undefined) ?? null,
    outline: () => (e.motion.selectedShown && e.motion.select.value > 0.001 ? { node: e.motion.selectedShown, strength: e.motion.select.value } : null),
    cameraDistance: () => {
      const v = first()
      return v ? v.camera.position.distanceTo(v.controls.target) : 0
    },
    preset: () => e.props?.preset ?? 'three-quarter',
    explode: () => e.explodeNow,
  }
  return api
}

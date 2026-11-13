// Makes one view and wires it to the engine: orbit events, picking, and loading the model (or the slab).
import type * as THREE from 'three'
import type { StageEngine } from './engine'
import { loadModel } from './loader'
import type { KindMaterials } from './materials'
import { bindPick } from './picking'
import type { StageProps, ViewSpec } from './types'
import { innerState } from './motion'
import { StageView } from './view'

export function createView(e: StageEngine, spec: ViewSpec, el: HTMLElement, props: StageProps, env: THREE.Texture, mats: KindMaterials): StageView {
  const v = new StageView(spec, el, env, mats, e.autoRotate)
  v.lastPreset = props.preset ?? 'three-quarter'
  v.controls.addEventListener('end', () => {
    e.active = false
    e.hardUntil = performance.now() + 800
  })
  v.controls.addEventListener('start', () => {
    e.active = true
    e.setAutoRotate(false)
    v.touched = true
    v.anim = null
  })
  v.controls.addEventListener('change', () => e.orbitChanged(performance.now()))
  // the ring holds still while the pointer is over it, so what is under the pointer is what a click gets
  v.el.addEventListener('pointerenter', () => {
    v.controls.autoRotate = false
    v.controls.enableDamping = false // flush the inertia of the last turn: the ring stops at once
  })
  v.el.addEventListener('pointerleave', () => {
    v.controls.autoRotate = e.autoRotate
    v.controls.enableDamping = true
  })
  v.el.addEventListener('pointerdown', () => (v.controls.enableDamping = true))
  e.views.set(spec.id, v)
  bindPick(v, () => e.props, () => e.explodeNow < 0.05, (h) => e.hover(h), (ev) => e.relative(ev))
  const done = (model: THREE.Object3D | null, innerModel: THREE.Object3D | null = null) => {
    if (e.views.get(spec.id) !== v) return // dropped while loading
    if (spec.role === 'exterior') e.face.size(props.ringModel)
    try {
      v.build(model, innerModel, props.ringModel, props.placements)
    } catch {
      v.fail()
    }
    if (e.renderer && v.state === 'ok') v.warm(e.renderer)
    v.lastPreset = e.props?.preset ?? v.lastPreset
    v.setPreset(v.lastPreset, true)
    v.applyMotion(innerState(e.motion))
    e.update(e.props ?? props, e.elFor)
    v.resize(el.clientWidth, el.clientHeight)
  }
  const inner = spec.inner ? loadModel(spec.inner.model).catch(() => null) : Promise.resolve(null)
  if (spec.slab || !spec.model) void inner.then((im) => done(null, im))
  else void Promise.all([loadModel(spec.model), inner]).then(([m, im]) => done(m, im), () => (v.fail(), e.notify()))
  e.notify()
  return v
}

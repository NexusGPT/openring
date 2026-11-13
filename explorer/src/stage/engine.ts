// The stage engine: ONE WebGL renderer for the whole page, N views drawn side by side into it with
// scissor rectangles. It is a module singleton, so a route change never creates a second context.
import * as THREE from 'three'
import type { PartPlacements, RingModel } from '../contract'
import { makeEnvironment } from './environment'
import { makeMaterials, type KindMaterials } from './materials'
import { createView } from './createView'
import { drawViews, measure, type Rect } from './draw'
import { FaceTexture } from './faceTexture'
import { Tween, smooth01 } from './ease'
import { APPEAR_AT } from './inner'
import { LID_MS, newMotion, stepMotion } from './motion'
import { makeRenderer } from './renderer'
import type { StageHover, StageProps, ViewPreset, ViewSpec } from './types'
import { StageView } from './view'

const statusOf = (views: Iterable<StageView>): string => [...views].map((v) => `${v.spec.id}:${v.state}`).join('|')

export class StageEngine {
  readonly canvas = document.createElement('canvas')
  readonly renderer: THREE.WebGLRenderer | null
  readonly views = new Map<string, StageView>()
  frames = 0
  ready = false
  autoRotate: boolean
  props: StageProps | null = null
  motion = newMotion()
  get explodeNow(): number {
    return this.motion.explode.value
  }
  private env: THREE.Texture | null = null
  private mats: KindMaterials | null = null
  face = new FaceTexture()
  rects = new Map<string, Rect>()
  host: HTMLElement | null = null
  private ro: ResizeObserver | null = null
  dirty = 3
  /** a pointer is on the orbit controls; hardUntil: damping after release still answers the user */
  active = false
  hardUntil = 0
  ambient = false
  private rafMs = 16
  private lastRaf = 0
  private lastRender = 0
  private cbs = new Set<() => void>()
  elFor = new Map<string, HTMLElement>()
  private lastStatus = ''
  private sizeKey = ''

  constructor() {
    this.autoRotate = !(typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches)
    this.canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block;pointer-events:none'
    const r = makeRenderer(this.canvas)
    if (r) {
      this.env = makeEnvironment(r)
      this.mats = makeMaterials(this.face.texture)
    }
    this.renderer = r
    if (r) requestAnimationFrame((t) => this.loop(t))
  }

  subscribe(cb: () => void): () => void {
    this.cbs.add(cb)
    return () => this.cbs.delete(cb)
  }
  status(): string {
    return this.renderer ? statusOf(this.views.values()) : 'webgl:failed'
  }

  attach(host: HTMLElement): void {
    this.host = host
    host.prepend(this.canvas)
    this.ro?.disconnect()
    if (typeof ResizeObserver === 'function') {
      this.ro = new ResizeObserver(() => this.layout())
      this.ro.observe(host)
    }
    this.layout()
  }
  detach(host: HTMLElement): void {
    if (this.host !== host) return
    this.ro?.disconnect()
    this.canvas.remove()
    this.host = null
  }

  /** Called by the React host after layout: the DOM regions of the views, then the props. */
  update(props: StageProps, els: ReadonlyMap<string, HTMLElement>): void {
    this.props = props
    if (!this.renderer || !this.mats) return
    this.elFor = new Map(els)
    if (this.built.ring !== props.ringModel || this.built.placements !== props.placements) {
      for (const id of [...this.views.keys()]) this.drop(id)
      this.built = { ring: props.ringModel, placements: props.placements }
    }
    for (const [id, v] of this.views) {
      const spec = props.views.find((s) => s.id === id)
      if (!spec || this.elFor.get(id) !== v.el || modelKey(spec) !== modelKey(v.spec)) this.drop(id)
    }
    for (const spec of props.views) {
      const el = this.elFor.get(spec.id)
      if (el && !this.views.has(spec.id)) this.add(spec, el, props)
      const v = this.views.get(spec.id)
      if (v) v.spec = spec
    }
    this.mats.setFinish(props.finish)
    this.mats.setLight(!!props.lightOn)
    const now = performance.now()
    const m = this.motion
    m.explode.set(props.explode ?? 0, now)
    m.appear.set(smooth01(props.explode ?? 0, 0, APPEAR_AT), now)
    if (props.isolatedLayer) {
      m.isolated = props.isolatedLayer
      m.iso.set(1, now)
    } else m.iso.set(0, now)
    const sel = props.selectedNode ?? null
    if (sel !== m.selectedShown && sel) {
      m.selectedShown = sel
      m.select.jump(0)
    }
    m.select.set(sel ? 1 : 0, now)
    const preset = props.preset ?? 'three-quarter'
    for (const v of this.views.values()) {
      v.applyProps(props)
      if (v.spec.lid) {
        const t = this.motion.lid.get(v.spec.id) ?? new Tween(0)
        this.motion.lid.set(v.spec.id, t)
        t.set(v.spec.lid.openDeg, now, LID_MS)
      }
      if (v.lastPreset !== preset && v.state === 'ok') {
        v.lastPreset = preset
        v.touched = false
        v.setPreset(preset, false)
        this.setAutoRotate(false)
      }
    }
    this.drawFace(true)
    this.layout()
    this.dirty = 3
    this.notify()
  }
  private built: { ring: RingModel | null; placements: PartPlacements | null } = { ring: null, placements: null }

  private add(spec: ViewSpec, el: HTMLElement, props: StageProps): void {
    if (this.renderer && this.env && this.mats) createView(this, spec, el, props, this.env, this.mats)
  }

  /** the Stage component sets this; it draws the name tag and calls props.onHover */
  hoverCb: ((h: StageHover | null) => void) | null = null
  hover(h: StageHover | null): void {
    this.hoverCb?.(h)
  }
  relative(e: PointerEvent): { x: number; y: number } {
    const b = this.host?.getBoundingClientRect()
    return { x: e.clientX - (b?.left ?? 0), y: e.clientY - (b?.top ?? 0) }
  }

  private drop(id: string): void {
    this.views.get(id)?.dispose()
    this.views.delete(id)
    this.rects.delete(id)
  }

  private drawFace(force: boolean): void {
    const faced = [...this.views.values()].some((v) => v.face?.visible && v.state === 'ok')
    if (this.face.draw(this.props?.ringModel ?? null, this.props?.screenState, faced, force, this.props?.elapsedSec)) {
      if (force) this.dirty = Math.max(this.dirty, 1)
      else this.ambient = true
    }
  }

  setAutoRotate(on: boolean): void {
    this.autoRotate = on
    for (const v of this.views.values()) v.controls.autoRotate = on
  }

  private layout(): void {
    const m = this.host && this.renderer ? measure(this.host, this.views) : null
    if (!m || !this.renderer) return
    if (`${m.w}x${m.h}` !== this.sizeKey) {
      this.renderer.setSize(m.w, m.h, false)
      this.sizeKey = `${m.w}x${m.h}`
    }
    this.rects = m.rects
    for (const [id, v] of this.views) v.resize(m.rects.get(id)?.w ?? 0, m.rects.get(id)?.h ?? 0)
    this.dirty = 3
  }

  notify(): void {
    const s = this.status()
    if (s === this.lastStatus) return
    this.lastStatus = s
    for (const cb of this.cbs) cb()
  }

  private loop(now: number): void {
    requestAnimationFrame((t) => this.loop(t))
    this.rafMs = 0.9 * this.rafMs + 0.1 * Math.min(1000, now - this.lastRaf)
    this.lastRaf = now
    const { moving, orbit } = stepMotion(this.motion, this.views.values(), now)
    this.drawFace(false)
    // Frames that answer the user or an eased change are drawn at once. Ambient frames (auto-rotate, the animated
    // screen face) are drawn at most every 4 frame times, so a slow machine or a heavy model keeps room for
    // clicks and screenshots: nothing is drawn when nothing moves.
    const hard = moving || this.dirty > 0 || this.active || now < this.hardUntil
    const ambient = this.ambient || orbit
    if (!hard && !(ambient && now - this.lastRender >= Math.max(33, Math.min(600, this.rafMs * 4)))) return
    this.dirty = Math.max(0, this.dirty - 1)
    this.ambient = false
    this.lastRender = now
    this.render()
  }

  /** The orbit controls changed: by the user (hard) or by themselves (ambient). */
  orbitChanged(now: number): void {
    if (this.active || now < this.hardUntil) this.dirty = Math.max(this.dirty, 1)
    else this.ambient = true
  }

  private render(): void {
    if (!this.renderer) return
    const drew = drawViews(this.renderer, this.views, this.rects)
    this.frames++
    if (drew) this.ready = true
    this.notify()
  }
}

/** What makes a view rebuild: its model and its node map (compared by content, never by reference). */
const modelKey = (s: ViewSpec): string => `${s.role}|${s.slab ? 'slab' : (s.model?.url ?? '')}|${s.inner?.model.url ?? ''}|${s.inner?.nodes.length ?? 0}|${s.nodes.map((n) => `${n.name}:${n.kind}:${n.layer ?? ''}`).join(',')}`

export { contextCount } from './renderer'
let engine: StageEngine | null = null
export function getEngine(): StageEngine {
  return (engine ??= new StageEngine())
}

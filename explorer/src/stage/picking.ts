// Click-to-pick and hover cursor for one view: a press and release without a drag picks the part under it.
import * as THREE from 'three'
import type { StageHover, StageProps } from './types'
import type { StageView } from './view'

export function bindPick(v: StageView, props: () => StageProps | null, assembled: () => boolean, hover: (h: StageHover | null) => void, rel: (e: PointerEvent) => { x: number; y: number }): void {
  let down: { x: number; y: number; t: number } | null = null
  const ray = new THREE.Raycaster()
  const at = (e: PointerEvent): string | null => {
    const b = v.el.getBoundingClientRect()
    ray.setFromCamera(new THREE.Vector2(((e.clientX - b.left) / b.width) * 2 - 1, -(((e.clientY - b.top) / b.height) * 2 - 1)), v.camera)
    const hits = ray.intersectObjects([...v.parts.values()].filter((p) => p.obj.visible && !p.ghost).flatMap((p) => p.meshes), false)
    // assembled, the cover glass is a window: the click goes to the part behind it (the lit area is the screen)
    const hit = (assembled() ? hits.find((h) => v.parts.get(v.partOf(h.object) ?? '')?.kind !== 'glass') : undefined) ?? hits[0]
    return hit ? v.partOf(hit.object) : null
  }
  v.el.addEventListener('pointerdown', (e) => (down = { x: e.clientX, y: e.clientY, t: e.timeStamp }))
  v.el.addEventListener('pointerup', (e) => {
    const d = down
    down = null
    const p = props()
    if (!d || !p?.onPick || Math.hypot(e.clientX - d.x, e.clientY - d.y) > 5 || e.timeStamp - d.t > 500) return
    const node = at(e)
    p.onPick(node ? { viewId: v.spec.id, node } : null)
  })
  let queued = false
  let shown: string | null = null
  v.el.addEventListener('pointermove', (e) => {
    if (e.buttons || queued) return
    queued = true
    requestAnimationFrame(() => {
      queued = false
      const node = at(e)
      v.el.style.cursor = node && props()?.onPick ? 'pointer' : 'grab'
      if (node || shown) hover(node ? { viewId: v.spec.id, node, ...rel(e) } : null)
      shown = node
    })
  })
  v.el.addEventListener('pointerleave', () => {
    shown = null
    hover(null)
  })
}

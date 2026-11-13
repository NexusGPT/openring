// Helpers that turn bundle records into view specs. The URL builders are the app's own (src/data/urls).
import type { Case, RingModel } from '../contract'
import { dataUrl, fileUrl } from '../data/urls'
import { caseNodeSpecs } from './caseKinds'
import type { ExteriorState, ViewSpec } from './types'

/** The ring's exterior. An approved model is `picked`; a model that is not approved yet but has a file is
 *  shown as `in-design` (a screen labels it); only when no file exists is it the plain black slab (`none`). */
export function exteriorView(ring: RingModel, id = 'exterior', label?: string): ViewSpec {
  const file = ring.exterior.file
  const exterior: ExteriorState = !file ? 'none' : ring.exterior.status === 'picked' ? 'picked' : 'in-design'
  return { id, role: 'exterior', model: file ? { url: dataUrl(file) } : null, slab: !file, exterior, nodes: ring.nodes, label }
}

/** The ring as everywhere: the exterior (or the slab) with the inside model hidden in it. The inside appears as the
 *  control opens; the same view serves Home and Inside, so the camera and the first frame never change between them. */
export function ringView(ring: RingModel, id = 'ring'): ViewSpec {
  const outer = exteriorView(ring, id)
  return ring.internals.file ? { ...outer, inner: { model: { url: dataUrl(ring.internals.file) }, nodes: ring.nodes } } : outer
}

/** One look option's model (a design file listed in files.json), shown as an exterior. */
export function lookView(ring: RingModel, option: { id: string; title: string; glb: { file: string } | null }): ViewSpec {
  return { id: option.id, role: 'exterior', model: option.glb ? { url: fileUrl(option.glb.file) } : null, slab: false, nodes: ring.nodes, label: option.title }
}

export function internalsView(ring: RingModel, id = 'internals'): ViewSpec {
  return { id, role: 'internals', model: ring.internals.file ? { url: dataUrl(ring.internals.file) } : null, nodes: ring.nodes }
}

export function caseView(c: Case, id = 'case'): ViewSpec | null {
  if (!c.glb) return null
  const hinge = c.glb.hinge
  return {
    id,
    role: 'case',
    model: { url: dataUrl(c.glb.file) },
    nodes: caseNodeSpecs(c.glb.nodes),
    lid: hinge ? { node: c.glb.lid_node, point: hinge.point, axis: hinge.axis, openDeg: 0 } : undefined,
  }
}

// The stage's public shapes. A screen describes WHAT to show; the stage decides how it looks.
// Every name, size, colour class and screen field comes from the data bundle records passed in.
import type { Kind, PartPlacements, RingModel, Vec3 } from '../contract'

export type ViewPreset = 'three-quarter' | 'top' | 'side' | 'finger'
export const VIEW_PRESETS: readonly ViewPreset[] = ['three-quarter', 'top', 'side', 'finger']

/** What a view shows. `exterior` gets the lit screen and the finger; `internals` gets layers and
 *  explode; `case` gets the lid. */
export type ExteriorState = 'picked' | 'in-design' | 'none'

export type ViewRole = 'exterior' | 'internals' | 'case'

export interface ViewModel {
  /** URL from dataUrl() or fileUrl(); the stage never builds one. */
  url: string
  format?: 'glb' | 'stl'
}

export interface NodeSpec {
  name: string
  kind: Kind
  layer?: string | null
  /** material class for this node (classMaterials.ts), when the caller knows it better than the kind */
  materialClass?: string
}

export interface LidSpec {
  node: string
  /** hinge point and axis in design coordinates (mm), as in the case record */
  point: Vec3
  axis: Vec3
  openDeg: number
}

export interface ViewSpec {
  /** look option id, or any stable id the caller wants back in onPick and in window.__stage */
  id: string
  role: ViewRole
  /** null with `slab: true` = the plain black slab; null otherwise = nothing to load */
  model: ViewModel | null
  /** plain black slab at the ring's true size (ring-model block); used while no exterior is picked */
  slab?: boolean
  /** node-to-kind map for this model; for the ring it is ringModel.nodes */
  nodes: readonly NodeSpec[]
  lid?: LidSpec
  /** the inside model hidden in this exterior; it appears as the ring opens (the composite ring) */
  inner?: { model: ViewModel; nodes: readonly NodeSpec[] }
  /** exterior views: `picked` (approved model), `in-design` (a model that is not approved yet), `none` (no model file: the plain black slab) */
  exterior?: ExteriorState
  /** a short caption drawn as React text above the view */
  label?: string
}

export interface FinishSpec {
  colour: string
  roughness: number
}

export interface StageProps {
  views: readonly ViewSpec[]
  /** ring-model record: block, band, screens. null = not available (screen face stays black). */
  ringModel: RingModel | null
  /** part-placements record: layers (order, z range, optional explode direction). */
  placements: PartPlacements | null
  finish?: FinishSpec | null
  /** a state id of ringModel.screens.states; null or unknown = screen off (black) */
  screenState?: string | null
  lightOn?: boolean
  /** seconds of the recording, from the screen that owns the clock; the screen's timer shows it as mm:ss */
  elapsedSec?: number | null
  preset?: ViewPreset
  /** 0 assembled .. 1 fully opened */
  explode?: number
  isolatedLayer?: string | null
  selectedNode?: string | null
  /** a part is under the pointer (or not: null). x, y are CSS px inside the stage. */
  onHover?: (hover: StageHover | null) => void
  /** display name per node name, drawn as the hover tag; no entry = no tag */
  labels?: Readonly<Record<string, string>>
  onPick?: (pick: { viewId: string; node: string } | null) => void
  /** shown over the stage when there is nothing to draw (a record is missing or unreadable) */
  notice?: import('../contract').BannerSpec | null
  /** test-id scope for the placeholder banner */
  route?: import('../contract').TestScope
  className?: string
}

/** A layer as the stage reads it: the record's fields plus the optional direction (see layers.ts). */
export type LayerRecord = PartPlacements['layers'][number] & { explode?: Vec3 | 'radial' | null; ghost_when_open?: boolean | null }

export interface StageHover {
  viewId: string
  node: string
  x: number
  y: number
}

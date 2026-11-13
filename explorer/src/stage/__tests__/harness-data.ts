// Made-up records for the stage harness and the stage unit tests. These are test data: the stage
// reads node names, kinds, layers, sizes and screen fields only from records shaped like these.
import type { PartPlacements, RingModel } from '../../contract'
import type { ViewSpec } from '../types'
import exteriorUrl from './models/exterior.glb?url'
import internalsUrl from './models/internals-meshopt.glb?url'

const src = { file: 'harness/made-up.md', line: 1 }

const n = (name: string, kind: RingModel['nodes'][number]['kind'], layer: string | null = null): RingModel['nodes'][number] => ({ name, kind, layer, part_ids: [] })

export const EXTERIOR_NODES: RingModel['nodes'] = [
  n('body', 'finish metal'),
  n('glass', 'glass'),
  n('screen', 'screen'),
  n('band', 'finish metal'),
  n('joystick', 'satin'),
  n('button', 'satin'),
  n('light', 'light'),
  n('mic_1', 'matte'),
  n('mic_2', 'matte'),
  n('contacts', 'gold'),
]

export const INTERNAL_NODES: RingModel['nodes'] = [
  n('glass', 'glass', 'l-top'),
  n('screen', 'screen', 'l-top'),
  n('light', 'light', 'l-top'),
  n('joystick', 'satin', 'l-mid'),
  n('button', 'satin', 'l-mid'),
  n('mic_1', 'matte', 'l-mid'),
  n('mic_2', 'matte', 'l-mid'),
  n('mic_3', 'matte', 'l-mid'),
  n('mic_4', 'matte', 'l-mid'),
  n('contacts', 'gold', 'l-mid'),
  n('body', 'finish metal', 'l-body'),
  n('band', 'finish metal', 'l-band'),
]

export const PICTURE: NonNullable<RingModel['screens']['states'][number]['pictures']>[number] = {
  name: 'rec-picture', file: 'screens/rec-picture.png', width: 240, height: 120, scale: 4, sha256: 'a'.repeat(64), scene: 'made-up scene', source: src,
}

const field = (id: string, kind: 'text' | 'dot' | 'timer' | 'battery' | 'storage' | 'bar' | 'icon', label: string | null) => ({ id, kind, label, source: src })

export const RING: RingModel = {
  design_version: 'H1',
  exterior: { status: 'picked', look_id: 'h-look', file: exteriorUrl, source: src },
  internals: { file: internalsUrl, node_count: INTERNAL_NODES.length, source: src },
  nodes: EXTERIOR_NODES,
  block: { size_mm: { x: 29.3, y: 14.8, z: 3.2 }, source: src },
  band: { width_mm: 8, inner_diameter_mm: 18.95, source: src },
  screens: {
    rect: { cx: 1.475, cy: 0, w: 21.6, h: 10.8, source: src },
    states: [
      { state: 'rec', label: 'Recording', source: src, pictures: [PICTURE], fields: [field('d', 'dot', 'Recording'), field('t', 'timer', null), field('b', 'battery', null), field('w', 'bar', null), field('s', 'storage', 'Storage free')] },
      { state: 'idle', label: 'Idle', source: src, picture_words: 'The ring software has no picture for this screen.', fields: [field('c', 'text', 'Clock'), field('b', 'battery', 'Battery')] },
    ],
  },
}

export const PLACEMENTS: PartPlacements = {
  layers: [
    { id: 'l-band', label: 'Band', order: 0, z_min: -4, z_max: 0, source: src, explode: { x: 0, y: 0, z: -1 } } as PartPlacements['layers'][number],
    { id: 'l-body', label: 'Body', order: 1, z_min: 0, z_max: 1.2, source: src },
    { id: 'l-mid', label: 'Parts', order: 2, z_min: 1.2, z_max: 2.7, source: src },
    { id: 'l-top', label: 'Glass', order: 3, z_min: 2.7, z_max: 3.2, source: src },
  ],
  placements: [],
}

export const FINISH = { colour: '#14151a', roughness: 0.24 }
export const FINISH_ALT = { colour: '#c99a52', roughness: 0.24 }

export const exteriorSpec = (id = 'exterior'): ViewSpec => ({ id, role: 'exterior', model: { url: exteriorUrl }, nodes: EXTERIOR_NODES })
export const internalsSpec = (): ViewSpec => ({ id: 'internals', role: 'internals', model: { url: internalsUrl }, nodes: INTERNAL_NODES })
export const slabSpec = (): ViewSpec => ({ id: 'slab', role: 'exterior', model: null, slab: true, nodes: [] })
export const brokenSpec = (): ViewSpec => ({ id: 'broken', role: 'exterior', model: { url: '/stage-harness/no-such-file.glb' }, nodes: EXTERIOR_NODES })

/** The layers of the real bundle as last collected (5 layers, explode vectors or radial); used when the live bundle has none. */
export const REAL_LAYERS: PartPlacements = {
  layers: [
    { id: 'body', label: 'body', order: 0, z_min: 0, z_max: 3.2, source: src, explode: { x: 0, y: 0, z: -1 } },
    { id: 'band', label: 'band', order: 1, z_min: -21.95, z_max: 1.45, source: src, explode: 'radial' },
    { id: 'board', label: 'board', order: 2, z_min: 0.45, z_max: 1.75, source: src, explode: { x: 0, y: 0, z: 1 } },
    { id: 'screen', label: 'screen', order: 3, z_min: 1.25, z_max: 2.65, source: src, explode: { x: 0, y: 0, z: 1 } },
    { id: 'glass', label: 'glass', order: 4, z_min: 2.65, z_max: 3.15, source: src, explode: { x: 0, y: 0, z: 1 } },
  ],
  placements: [],
}

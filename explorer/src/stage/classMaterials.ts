// One table: material class -> material, for the parts of the inside model. The class names come from
// the bundle (children named <part>__<class>); until the model carries them, the existing node kinds map
// to a class through KIND_CLASS. All of them sit in the same studio light as the exterior.
import * as THREE from 'three'
import type { Kind } from '../contract'

export const CLASSES = ['metal', 'gold', 'pcb', 'chip', 'ceramic', 'polymer', 'glass', 'screen', 'foam', 'flex', 'cell', 'resin', 'mark', 'satin', 'soft'] as const
export type MaterialClass = (typeof CLASSES)[number]

export const KIND_CLASS: Record<Kind, MaterialClass> = {
  'finish metal': 'metal', glass: 'glass', screen: 'screen', light: 'resin', satin: 'metal', matte: 'polymer', gold: 'gold', plain: 'polymer',
}

const std = (color: number, roughness: number, metalness: number, extra: THREE.MeshPhysicalMaterialParameters = {}) =>
  new THREE.MeshPhysicalMaterial({ color, roughness, metalness, envMapIntensity: 1, ...extra })

const TABLE: Record<MaterialClass, () => THREE.MeshPhysicalMaterial> = {
  metal: () => std(0xb9bec5, 0.36, 1, { clearcoat: 0.15 }), // brushed light metal
  gold: () => std(0xd9ae4c, 0.22, 1, { clearcoat: 0.3 }),
  pcb: () => std(0x123f2c, 0.5, 0, { clearcoat: 0.35, clearcoatRoughness: 0.4 }), // deep green solder mask
  chip: () => std(0x1c1e22, 0.42, 0.25, { clearcoat: 0.2 }), // dark satin
  ceramic: () => std(0xe7e2d8, 0.32, 0),
  polymer: () => std(0x5d636b, 0.55, 0.05, { clearcoat: 0.1 }),
  glass: () => std(0x0a0b0d, 0.05, 0, { clearcoat: 0.6, clearcoatRoughness: 0, ior: 1.5, specularIntensity: 0.5, envMapIntensity: 0.6 }),
  screen: () => std(0x050506, 0.18, 0, { clearcoat: 0.5, clearcoatRoughness: 0.05 }),
  foam: () => std(0xcfc6b2, 0.95, 0),
  flex: () => std(0xc98b2a, 0.38, 0.1, { clearcoat: 0.4, sheen: 0.4 }), // amber-tinted film
  cell: () => std(0xc8cbd0, 0.62, 0.65), // matte silver pouch
  resin: () => std(0xd9d2c3, 0.4, 0, { clearcoat: 0.3 }),
  mark: () => std(0x141517, 0.8, 0),
  satin: () => std(0xc9ccd0, 0.46, 1, { clearcoat: 0.04, clearcoatRoughness: 0.6 }), // bead-blasted light metal: the case's outer shell
  soft: () => std(0x202226, 0.88, 0, { sheen: 0.35, sheenRoughness: 0.7 }), // dark soft-touch insert: where the ring rests
}

export interface ClassMaterials {
  /** a fresh material of the class (each part clones its own, so its opacity is its own) */
  make(cls: MaterialClass): THREE.MeshPhysicalMaterial
  has(name: string): name is MaterialClass
}

export const classMaterials: ClassMaterials = {
  make: (cls) => TABLE[cls](),
  has: (name): name is MaterialClass => (CLASSES as readonly string[]).includes(name),
}

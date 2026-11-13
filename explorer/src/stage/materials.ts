// One material per node KIND. The kind of every node comes from the bundle (ring-model.nodes);
// nothing here names a part. One set is shared by every view, so there is one screen texture
// per WebGL context.
import * as THREE from 'three'
import type { Kind } from '../contract'
import type { FinishSpec } from './types'

export const ACCENT = 0xc24e00
const FALLBACK_FINISH: FinishSpec = { colour: '#14151a', roughness: 0.24 }

export interface KindMaterials {
  byKind: Record<Kind, THREE.Material>
  screenFace: THREE.MeshBasicMaterial
  light: THREE.MeshStandardMaterial
  highlight: Record<Kind, THREE.Material>
  setFinish(f: FinishSpec | null | undefined): void
  setLight(on: boolean): void
  dispose(): void
}

export function makeMaterials(screenTexture: THREE.Texture): KindMaterials {
  const metal = new THREE.MeshPhysicalMaterial({ color: FALLBACK_FINISH.colour, metalness: 1, roughness: FALLBACK_FINISH.roughness, clearcoat: 0.6, clearcoatRoughness: 0.08, envMapIntensity: 1 })
  const satin = new THREE.MeshPhysicalMaterial({ color: 0x777777, metalness: 1, roughness: 0.42, clearcoat: 0, envMapIntensity: 1 })
  const glass = new THREE.MeshPhysicalMaterial({ color: 0x050506, metalness: 0, roughness: 0.05, clearcoat: 0.35, clearcoatRoughness: 0, ior: 1.5, specularIntensity: 0.4, envMapIntensity: 0.3 })
  const light = new THREE.MeshStandardMaterial({ color: 0x300000, emissive: 0xff2020, emissiveIntensity: 0.15, roughness: 0.4 })
  const matte = new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 0.95, metalness: 0 })
  const gold = new THREE.MeshPhysicalMaterial({ color: 0xe6b84a, metalness: 1, roughness: 0.15, clearcoat: 0.3, envMapIntensity: 1.6 })
  const plain = new THREE.MeshStandardMaterial({ color: 0x80868f, roughness: 0.5, metalness: 0.1 })
  // the lit picture: unlit, additive, outside tone mapping, so black adds nothing and the glass shows through
  const screenFace = new THREE.MeshBasicMaterial({ map: screenTexture, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 })
  screenFace.color.setScalar(1)
  const byKind: Record<Kind, THREE.Material> = { 'finish metal': metal, satin, glass, screen: glass, light, matte, gold, plain }
  const highlight = {} as Record<Kind, THREE.Material>
  for (const k of Object.keys(byKind) as Kind[]) {
    const m = byKind[k].clone() as THREE.MeshStandardMaterial
    m.emissive = new THREE.Color(ACCENT)
    m.emissiveIntensity = 0.3
    highlight[k] = m
  }
  return {
    byKind,
    highlight,
    screenFace,
    light,
    setFinish(f) {
      const fin = f ?? FALLBACK_FINISH
      metal.color.set(fin.colour)
      metal.roughness = fin.roughness
      satin.color.set(fin.colour).lerp(new THREE.Color(0xffffff), 0.18)
      for (const k of ['finish metal', 'satin'] as const) (highlight[k] as THREE.MeshStandardMaterial).color.copy((byKind[k] as THREE.MeshStandardMaterial).color)
    },
    setLight(on) {
      light.emissiveIntensity = on ? 3.2 : 0.15
      ;(highlight.light as THREE.MeshStandardMaterial).emissiveIntensity = on ? 3.2 : 0.3
    },
    dispose() {
      for (const m of [...Object.values(byKind), ...Object.values(highlight), screenFace]) m.dispose()
    },
  }
}

/** css colour of a material as '#rrggbb' (the highlight copy reports the base colour). */
export function materialHex(m: THREE.Material | THREE.Material[] | null | undefined): string | null {
  const one = Array.isArray(m) ? m[0] : m
  const c = (one as THREE.MeshStandardMaterial | undefined)?.color
  return c ? `#${c.getHexString()}` : null
}

// The exterior as the shell of the composite ring: its materials are the view's own copies, so fading it
// (opacity 1 -> 0 as the ring opens) never touches another view. The copies follow the shared ones (finish, light).
import * as THREE from 'three'

type Std = THREE.MeshStandardMaterial & Partial<THREE.MeshPhysicalMaterial>

export interface Shell {
  root: THREE.Object3D
  pairs: Array<{ src: Std; copy: Std }>
}

/** Replace every material under root by a view-owned copy. */
export function forkShell(root: THREE.Object3D): Shell {
  const copies = new Map<Std, Std>()
  const pairs: Shell['pairs'] = []
  root.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh || Array.isArray(mesh.material)) return
    const src = mesh.material as Std
    let c = copies.get(src)
    if (!c) {
      c = src.clone() as Std
      copies.set(src, c)
      pairs.push({ src, copy: c })
    }
    mesh.material = c
  })
  return { root, pairs }
}

export function fadeShell(s: Shell, opacity: number): void {
  s.root.visible = opacity > 0.001
  for (const { src, copy } of s.pairs) {
    copy.color.copy(src.color)
    copy.roughness = src.roughness
    copy.metalness = src.metalness
    copy.emissive.copy(src.emissive)
    copy.emissiveIntensity = src.emissiveIntensity
    copy.envMapIntensity = src.envMapIntensity
    copy.transparent = opacity < 0.999
    copy.opacity = opacity
    copy.depthWrite = opacity > 0.98
  }
}

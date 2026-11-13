// The plain black slab shown while no exterior is approved: one box at the ring's true block
// size, no detail. Size comes from ring-model.block (design x, y, z -> three x, z, y); the bottom is at y = 0.
import * as THREE from 'three'
import type { RingModel } from '../contract'

export function makeSlab(block: RingModel['block']['size_mm'], mat: THREE.Material): THREE.Group {
  const g = new THREE.Group()
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(block.x, block.z, block.y), mat)
  mesh.position.y = block.z / 2
  g.add(mesh)
  g.updateMatrixWorld(true)
  return g
}

export const slabMaterial = (): THREE.MeshPhysicalMaterial =>
  new THREE.MeshPhysicalMaterial({ color: 0x050506, metalness: 0, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 0.6 })

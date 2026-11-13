// Loads a model from a URL the caller built. GLB (metres, Y up, meshopt allowed) or STL (mm, Z up).
// The result is a group in millimetres, Y up. One download per url; each view gets its own clone.
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { STLLoader } from 'three/addons/loaders/STLLoader.js'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'
import type { ViewModel } from './types'

const cache = new Map<string, Promise<THREE.Object3D>>()

function formatOf(m: ViewModel): 'glb' | 'stl' {
  if (m.format) return m.format
  return /\.stl(\?|#|$)/i.test(m.url) ? 'stl' : 'glb'
}

async function fetchModel(m: ViewModel): Promise<THREE.Object3D> {
  const group = new THREE.Group()
  if (formatOf(m) === 'stl') {
    const geo = await new STLLoader().loadAsync(m.url)
    const mesh = new THREE.Mesh(geo)
    mesh.name = m.url.split('/').pop()?.replace(/\.stl.*$/i, '') ?? 'model'
    mesh.rotation.x = -Math.PI / 2
    group.add(mesh)
  } else {
    const loader = new GLTFLoader()
    loader.setMeshoptDecoder(MeshoptDecoder)
    const gltf = await loader.loadAsync(m.url)
    group.add(gltf.scene)
    // glTF is in metres unless the asset says its units are mm (asset.extras.units); the stage works in millimetres
    group.scale.setScalar(gltf.asset.extras?.units === 'mm' ? 1 : 1000)
  }
  group.updateMatrixWorld(true)
  return group
}

/** A fresh clone of the loaded model; geometry is shared, materials are replaced by the view. */
export async function loadModel(m: ViewModel): Promise<THREE.Object3D> {
  let p = cache.get(m.url)
  if (!p) {
    p = fetchModel(m)
    cache.set(m.url, p)
    p.catch(() => cache.delete(m.url))
  }
  return (await p).clone(true)
}

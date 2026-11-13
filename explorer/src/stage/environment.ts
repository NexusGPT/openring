// Studio lighting from the seed viewer (slim path): a room environment plus soft strips, so the
// glass and the polished metal show long soft reflections and no blown highlights.
import * as THREE from 'three'
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js'

export function radialTexture(stops: ReadonlyArray<readonly [number, string]>, size = 256): THREE.CanvasTexture {
  const c = document.createElement('canvas')
  c.width = c.height = size
  const g = c.getContext('2d')
  if (g) {
    const r = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
    for (const [o, col] of stops) r.addColorStop(o, col)
    g.fillStyle = r
    g.fillRect(0, 0, size, size)
  }
  const t = new THREE.CanvasTexture(c)
  t.colorSpace = THREE.SRGBColorSpace
  return t
}

export function makeEnvironment(renderer: THREE.WebGLRenderer): THREE.Texture {
  const pm = new THREE.PMREMGenerator(renderer)
  const env = new RoomEnvironment()
  const strip = (w: number, h: number, d: number, x: number, y: number, z: number, v: number) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshBasicMaterial({ color: new THREE.Color(v * 0.05, v * 0.05, v * 0.05) }))
    m.position.set(x, y, z)
    m.userData.strip = true
    env.add(m)
  }
  strip(34, 1.6, 0.6, 0, 9.4, 5.5, 70) // long soft strip along X: its reflection runs along the shoulder
  strip(34, 2.2, 0.5, -6.9, 4.7, -8.1, 90) // one long soft band along the glass
  strip(1, 9, 5, -8, 8, 4, 8)
  strip(1, 9, 5, 8, 8, -3, 5)
  strip(8, 0.5, 6, 6, 14, -5, 2.5) // top softbox, off-axis so a straight-down view does not mirror it
  strip(0.5, 10, 16, 11, 6, 0, 3.5)
  strip(0.5, 10, 16, -11, 6, 0, 2.5)
  strip(16, 10, 0.5, 0, 6, 11, 3)
  strip(16, 10, 0.5, 0, 6, -11, 2.5)
  env.traverse((o) => {
    const m = (o as THREE.Mesh).material as THREE.Material | undefined
    if (m && (m as THREE.MeshBasicMaterial).isMeshBasicMaterial && !o.userData.strip) (m as THREE.MeshBasicMaterial).color.multiplyScalar(0.12)
    if (m && (m as THREE.MeshStandardMaterial).isMeshStandardMaterial) (m as THREE.MeshStandardMaterial).color.multiplyScalar(0.4)
  })
  const tex = pm.fromScene(env, 0.035).texture
  pm.dispose()
  return tex
}

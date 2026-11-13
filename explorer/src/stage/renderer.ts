// The one WebGL renderer of the page: transparent canvas (clear colour white, alpha 0) over the page background.
import * as THREE from 'three'

export let contextCount = 0

/** null when the browser cannot make a WebGL context; the stage then says so in words. */
export function makeRenderer(canvas: HTMLCanvasElement): THREE.WebGLRenderer | null {
  try {
    const r = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' })
    contextCount++
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
    r.outputColorSpace = THREE.SRGBColorSpace
    r.toneMapping = THREE.ACESFilmicToneMapping
    r.toneMappingExposure = 1.05
    r.setClearColor(0xffffff, 0)
    return r
  } catch {
    return null
  }
}

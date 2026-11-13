// The screen face texture: one canvas and one texture for the whole page (one per WebGL context).
// It holds the picture of the chosen screen state (a file of the data bundle) and redraws only when what it shows changes.
import * as THREE from 'three'
import type { RingModel } from '../contract'
import { dataUrl } from '../data/urls'
import { drawFace, faceSize, findState, pictureOf } from './screenFace'

export class FaceTexture {
  readonly canvas = document.createElement('canvas')
  readonly texture: THREE.CanvasTexture
  private image: HTMLImageElement | null = null
  private imageFile: string | null = null
  private loaded = false
  /** what the canvas shows now: a picture file, null = black; undefined = nothing drawn yet */
  private shown: string | null | undefined = undefined

  constructor() {
    this.canvas.width = 960
    this.canvas.height = 480
    this.texture = new THREE.CanvasTexture(this.canvas)
    this.texture.colorSpace = THREE.SRGBColorSpace
    this.texture.anisotropy = 8
  }

  /** Match the canvas to the pictures of the record (before the first draw that uses it). */
  size(ring: RingModel | null): void {
    const first = ring?.screens.states.find((s) => pictureOf(s))
    const p = first ? pictureOf(first) : null
    if (p) this.fit(p)
  }

  private fit(p: Parameters<typeof faceSize>[0]): void {
    const { width, height } = faceSize(p)
    if (this.canvas.width !== width || this.canvas.height !== height) Object.assign(this.canvas, { width, height })
  }

  private want(file: string | null): void {
    if (!file || file === this.imageFile) return
    const img = new Image()
    this.image = img
    this.imageFile = file
    this.loaded = false
    img.onload = () => {
      if (this.image === img) this.loaded = true
    }
    img.src = dataUrl(file)
  }

  /** Redraw when forced or when what the face shows changed (a picture arrived, the state changed). Returns true when it drew.
   *  `visible` and `elapsed` are kept for the stage's call: a still picture needs neither. */
  draw(ring: RingModel | null, stateId: string | null | undefined, _visible: boolean, force: boolean, _elapsed?: number | null): boolean {
    const pic = pictureOf(findState(ring, stateId))
    this.want(pic?.file ?? null)
    const file = pic && this.loaded && this.imageFile === pic.file ? pic.file : null
    if (!force && file === this.shown) return false
    const c = this.canvas.getContext('2d')
    if (!c) return false
    if (pic) this.fit(pic)
    drawFace(c, this.canvas.width, this.canvas.height, file ? this.image : null)
    this.texture.needsUpdate = true
    this.shown = file
    return true
  }
}

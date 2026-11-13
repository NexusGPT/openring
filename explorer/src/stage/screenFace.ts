// The lit screen face. It shows the ring software's own picture of the chosen screen state, as the record lists it
// (ring-model screens.states[].pictures), and nothing else: no text, no mock, no timer. A state without a picture is a black face.
import type { RingModel } from '../contract'

export type ScreenStateRec = RingModel['screens']['states'][number]
export type ScreenPicture = NonNullable<ScreenStateRec['pictures']>[number]

export function findState(model: RingModel | null, id: string | null | undefined): ScreenStateRec | null {
  if (!model || !id) return null
  return model.screens.states.find((s) => s.state === id) ?? null
}

/** The labels the record lists for a state's fields, in record order, without the empty ones. They are data of the record; the glass never draws them. */
export function fieldLabels(state: ScreenStateRec | null): string[] {
  return (state?.fields ?? []).flatMap((f) => (f.label ? [f.label] : []))
}

/** The picture the glass shows for a state: the first one the record lists, or null. */
export function pictureOf(state: ScreenStateRec | null): ScreenPicture | null {
  return state?.pictures?.[0] ?? null
}

/** The record's words for a state that has no picture, or null. */
export function pictureWords(state: ScreenStateRec | null): string | null {
  return state?.picture_words ?? null
}

/** Canvas size of a picture: each of its pixels becomes scale x scale pixels, so 240 x 120 stays sharp and keeps its shape. */
export function faceSize(p: Pick<ScreenPicture, 'width' | 'height' | 'scale'>): { width: number; height: number } {
  return { width: p.width * p.scale, height: p.height * p.scale }
}

interface Ctx2D {
  fillStyle: string | CanvasGradient | CanvasPattern
  imageSmoothingEnabled: boolean
  fillRect(x: number, y: number, w: number, h: number): void
  drawImage(img: CanvasImageSource, x: number, y: number, w: number, h: number): void
}

/** Black, then the picture over the whole canvas with hard pixel edges. No picture = black only. */
export function drawFace(c: Ctx2D, W: number, H: number, picture: CanvasImageSource | null): void {
  c.fillStyle = '#000'
  c.fillRect(0, 0, W, H)
  if (!picture) return
  c.imageSmoothingEnabled = false
  c.drawImage(picture, 0, 0, W, H)
}

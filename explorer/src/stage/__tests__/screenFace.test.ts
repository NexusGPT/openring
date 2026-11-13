// screen-face-C10..C15: the glass face draws the ring software's own picture and no specification text.
import { describe, expect, it } from 'vitest'
import { PICTURE, RING } from './harness-data'
import { drawFace, faceSize, fieldLabels, findState, pictureOf, pictureWords } from '../screenFace'

const TEXT_CALLS = new Set(['fillText', 'strokeText', 'measureText'])

/** A 2D context that records every call and throws on any call that draws or measures text. */
function stubCtx() {
  const calls: string[] = []
  const props: Record<string, unknown> = {}
  const c = new Proxy(props, {
    get(t, k: string) {
      if (TEXT_CALLS.has(k)) throw new Error(`text drawn: ${k}`)
      if (k in t) return t[k]
      return (...a: unknown[]) => void calls.push(`${k}(${a.map((x) => (typeof x === 'object' ? 'obj' : String(x))).join(',')})`)
    },
    set(t, k: string, v) {
      t[k] = v
      return true
    },
  })
  return { c: c as never, calls, props }
}

describe('screen face (screen-face-C10 to C12)', () => {
  it('C10 the record states with a picture give it, the others give none, and a missing record gives none', () => {
    expect(pictureOf(findState(RING, 'rec'))).toBe(PICTURE)
    expect(pictureOf(findState(RING, 'idle'))).toBeNull()
    expect(pictureOf(findState(RING, 'nope'))).toBeNull()
    expect(pictureOf(findState(null, 'rec'))).toBeNull()
    expect(pictureWords(findState(RING, 'idle'))).toBe('The ring software has no picture for this screen.')
    expect(pictureWords(findState(RING, 'rec'))).toBeNull()
  })
  it('C11 draws the picture once, over the whole face with sharp pixels, on black, and not one word of text', () => {
    const { c, calls, props } = stubCtx()
    drawFace(c, 960, 480, { width: 240 } as unknown as CanvasImageSource)
    expect(calls).toEqual(['fillRect(0,0,960,480)', 'drawImage(obj,0,0,960,480)'])
    expect(props.imageSmoothingEnabled).toBe(false)
    expect(props.fillStyle).toBe('#000')
  })
  it('C12 a state without a picture is one black rectangle: no image, no text', () => {
    const { c, calls } = stubCtx()
    drawFace(c, 960, 480, null)
    expect(calls).toEqual(['fillRect(0,0,960,480)'])
  })
})

describe('the face keeps the true shape of the lit area (screen-face-C13)', () => {
  it('C13 the picture, scaled whole, has the aspect of the screen rectangle of the record: square pixels of 0.09 mm', () => {
    const { w, h } = RING.screens.rect
    const size = faceSize(PICTURE)
    expect(size).toEqual({ width: 960, height: 480 })
    expect(size.width / size.height).toBeCloseTo(w / h, 9)
    expect(w / PICTURE.width).toBeCloseTo(h / PICTURE.height, 9)
  })
})

describe('what the record lists is still reachable', () => {
  it('lists the labels of the record, in order, without empty ones (not drawn on the glass)', () => {
    expect(fieldLabels(findState(RING, 'rec'))).toEqual(['Recording', 'Storage free'])
    expect(fieldLabels(findState(RING, 'nope'))).toEqual([])
    expect(fieldLabels(findState(null, 'rec'))).toEqual([])
  })
})

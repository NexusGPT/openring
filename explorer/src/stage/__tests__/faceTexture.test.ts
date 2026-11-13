// screen-face-C14: the one face texture of the stage shows the picture of the chosen state, once, and never a mock.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { RING } from './harness-data'
import { FaceTexture } from '../faceTexture'

const TEXT = ['fillText', 'strokeText', 'measureText']
let log: string[]
let images: FakeImage[]
const first = (): FakeImage => {
  const i = images[0]
  if (!i) throw new Error('no picture was asked for')
  return i
}

class FakeImage {
  onload: (() => void) | null = null
  src = ''
  constructor() {
    images.push(this)
  }
}

beforeEach(() => {
  log = []
  images = []
  const props: Record<string, unknown> = {}
  const ctx = new Proxy(props, {
    get(t, k: string) {
      if (TEXT.includes(k)) throw new Error(`text drawn: ${k}`)
      if (k in t) return t[k]
      return (...a: unknown[]) => void log.push(`${k}(${a.map((x) => (x instanceof FakeImage ? `image:${x.src}` : typeof x === 'object' ? 'obj' : String(x))).join(',')})`)
    },
    set(t, k: string, v) {
      t[k] = v
      return true
    },
  })
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(ctx as never)
  vi.stubGlobal('Image', FakeImage)
})
afterEach(() => {
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('FaceTexture (screen-face-C14)', () => {
  it('C14a a state with a picture is black until the picture has loaded, then it draws that picture and no text; one load', () => {
    const f = new FaceTexture()
    expect(f.draw(RING, 'rec', true, true)).toBe(true)
    expect(log).toEqual(['fillRect(0,0,960,480)'])
    expect(images).toHaveLength(1)
    expect(first().src).toMatch(/data\/screens\/rec-picture\.png$/)
    expect(f.draw(RING, 'rec', true, false)).toBe(false) // still loading: nothing new to draw
    first().onload?.()
    log.length = 0
    expect(f.draw(RING, 'rec', true, false)).toBe(true)
    expect(log).toEqual(['fillRect(0,0,960,480)', `drawImage(image:${first().src},0,0,960,480)`])
    log.length = 0
    expect(f.draw(RING, 'rec', true, false)).toBe(false) // a still picture: no redraw, no timer
    expect(images).toHaveLength(1)
  })
  it('C14b the elapsed time of the recording is not drawn over the picture', () => {
    const f = new FaceTexture()
    f.draw(RING, 'rec', true, true, 75)
    first().onload?.()
    expect(() => f.draw(RING, 'rec', true, true, 76)).not.toThrow()
    expect(log.filter((x) => x.startsWith('drawImage'))).toHaveLength(1)
  })
  it('C14c a state without a picture, an unknown state, no state and no record draw black only', () => {
    const f = new FaceTexture()
    for (const [ring, id] of [[RING, 'idle'], [RING, 'nope'], [RING, null], [null, 'rec']] as const) {
      log.length = 0
      f.draw(ring, id, true, true)
      expect(log).toEqual(['fillRect(0,0,960,480)'])
    }
    expect(images).toHaveLength(0)
  })
  it('C14d going from a state with a picture to one without gives back a black face at once', () => {
    const f = new FaceTexture()
    f.draw(RING, 'rec', true, true)
    first().onload?.()
    f.draw(RING, 'rec', true, false)
    log.length = 0
    expect(f.draw(RING, 'idle', true, false)).toBe(true)
    expect(log).toEqual(['fillRect(0,0,960,480)'])
  })
})

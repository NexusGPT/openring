import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import { SvgViewer } from '..'
import { FIT, MAX_ZOOM, ZOOM_STEP, clampView, fitScale, parseViewBox, viewForRect, zoomAt } from '../model'

afterEach(cleanup)
const VB = [0, 0, 100, 60] as const
const viewer = () => screen.getByTestId('electronics.svg-viewer')
const scale = () => Number(viewer().getAttribute('data-scale'))
const mount = (extra = {}) => render(<SvgViewer route="electronics" src="/data/schematic/mics.svg" label="Microphone page" viewBox={VB} {...extra} />)
/** The layer's pixel shift [tx, ty] read from its style (jsdom prints a zero y as nothing). */
const layerShift = (): [number, number] => {
  const m = /translate\(-50%, -50%\) translate\(([-\d.]+)px(?:, ([-\d.]+)px)?\)/.exec(viewer().querySelector('.svgv-layer')?.getAttribute('style') ?? '')
  return [Number(m?.[1] ?? NaN), Number(m?.[2] ?? 0)]
}
const click = (name: string) => fireEvent.click(screen.getByTestId(`electronics.svg-viewer-${name}`))

describe('svg viewer', () => {
  it('svg-viewer-C01: four zoom-in presses read 4.0 (400 %), Fit gives 1.0', () => {
    mount()
    expect(scale()).toBe(1)
    for (let i = 0; i < 4; i++) click('zoom-in')
    expect(Math.abs(scale() - 4)).toBeLessThan(0.05)
    expect(screen.getByTestId('electronics.svg-viewer-scale').textContent).toBe('400 %')
    click('fit')
    expect(scale()).toBe(1)
    expect(layerShift()).toEqual([0, 0])
  })

  it('svg-viewer-C03: the picture is only ever an <img>; no inline svg, object, iframe or embed', () => {
    mount()
    const img = screen.getByTestId('electronics.svg-viewer-image')
    expect(img.tagName).toBe('IMG')
    expect(img.getAttribute('src')).toBe('/data/schematic/mics.svg')
    for (const tag of ['svg', 'object', 'iframe', 'embed', 'script']) expect(viewer().querySelector(tag)).toBeNull()
  })

  it('svg-viewer-C04: no picture gives the honest "missing" words, disabled buttons and no image', () => {
    const { unmount } = mount({ src: null })
    expect(screen.getByTestId('electronics.state-banner').textContent).toContain('Not built yet. Run npm run collect.')
    expect(screen.queryByTestId('electronics.svg-viewer-image')).toBeNull()
    for (const b of ['zoom-in', 'zoom-out', 'fit']) expect((screen.getByTestId(`electronics.svg-viewer-${b}`) as HTMLButtonElement).disabled).toBe(true)
    unmount()
    mount({ src: '/data/board/a.svg' })
    fireEvent.error(screen.getByTestId('electronics.svg-viewer-image'))
    expect(screen.getByTestId('electronics.state-banner').textContent).toContain('cannot be read: a.svg')
  })

  it('svg-viewer-C05: keys: + and - zoom, 0 fits, arrows pan', () => {
    mount()
    const stage = screen.getByRole('group', { name: 'Microphone page' })
    fireEvent.keyDown(stage, { key: '+' })
    fireEvent.keyDown(stage, { key: '=' })
    expect(Math.abs(scale() - 2)).toBeLessThan(0.001)
    fireEvent.keyDown(stage, { key: 'ArrowLeft' })
    expect(layerShift()).toEqual([60, 0])
    fireEvent.keyDown(stage, { key: '-' })
    expect(Math.abs(scale() - Math.SQRT2)).toBeLessThan(0.001)
    fireEvent.keyDown(stage, { key: '0' })
    expect(scale()).toBe(1)
    expect(layerShift()).toEqual([0, 0])
  })

  it('svg-viewer-C06: wheel up zooms in, about the pointer; the page does not scroll', () => {
    mount()
    const stage = screen.getByRole('group', { name: 'Microphone page' })
    const ev = new WheelEvent('wheel', { deltaY: -300, cancelable: true, bubbles: true })
    act(() => { stage.dispatchEvent(ev) })
    expect(ev.defaultPrevented).toBe(true)
    expect(scale()).toBeGreaterThan(1.4)
  })

  it('svg-viewer-C07: a focus rectangle zooms to it, outlines it, and jumps again when its id changes', () => {
    const r = { x: 40, y: 20, w: 12, h: 10, id: 'U5' }
    const { rerender } = mount({ focus: r })
    const z1 = scale()
    expect(z1).toBeGreaterThan(2)
    expect(screen.getByTestId('electronics.svg-viewer-focus').style.width).not.toBe('')
    click('fit')
    expect(scale()).toBe(1)
    rerender(<SvgViewer route="electronics" src="/data/schematic/mics.svg" label="Microphone page" viewBox={VB} focus={{ ...r, id: 'U5b' }} />)
    expect(scale()).toBeCloseTo(z1, 3)
  })
})

describe('svg viewer geometry', () => {
  const pic = { w: 100, h: 60 }, box = { w: 800, h: 600 }
  it('svg-viewer-C08: zoomAt keeps the point under the pointer still; zoom is clamped', () => {
    const v = zoomAt(FIT, 3, 120, -50)
    // the picture point under (120,-50) before: (120,-50) from centre / k; after: (120 - tx)/3
    expect((120 - v.tx) / 3).toBeCloseTo(120, 6)
    expect((-50 - v.ty) / 3).toBeCloseTo(-50, 6)
    expect(zoomAt(FIT, 1e6, 0, 0).z).toBe(MAX_ZOOM)
    expect(zoomAt(FIT, 0, 0, 0).z).toBeGreaterThan(0)
    expect(ZOOM_STEP ** 4).toBeCloseTo(4, 12)
  })
  it('svg-viewer-C09: viewForRect puts the rectangle centre on the box centre', () => {
    const r = { x: 40, y: 20, w: 12, h: 10 }
    const v = viewForRect(r, pic, { x: 0, y: 0 }, box)
    const k = fitScale(pic, box) * v.z
    expect(box.w / 2 + v.tx + (46 - 50) * k).toBeCloseTo(box.w / 2, 3)
    expect(box.h / 2 + v.ty + (25 - 30) * k).toBeCloseTo(box.h / 2, 3)
    expect(r.w * k).toBeLessThanOrEqual(box.w * 0.56)
    expect(viewForRect({ x: 0, y: 0, w: 0.0001, h: 0.0001 }, pic, { x: 0, y: 0 }, box).z).toBe(12)
    const off = viewForRect({ x: 5, y: 5, w: 1, h: 1 }, pic, { x: 0, y: 0 }, box)
    expect(box.w / 2 + off.tx + (5.5 - 50) * fitScale(pic, box) * off.z).toBeCloseTo(box.w / 2, 3)
  })
  it('svg-viewer-C10: clampView keeps part of the picture on screen; parseViewBox rejects junk', () => {
    const v = clampView({ z: 1, tx: 1e6, ty: -1e6 }, pic, box)
    expect(Math.abs(v.tx)).toBeLessThan(box.w)
    expect(parseViewBox('0 0 297.0022 210.0072')).toEqual([0, 0, 297.0022, 210.0072])
    expect(parseViewBox('0 0 0 5')).toBeNull()
    expect(parseViewBox('a b c d')).toBeNull()
  })
})

describe('svg viewer source rules', () => {
  const dir = join(__dirname, '..')
  const files = readdirSync(dir).filter((f) => /\.(tsx?|css)$/.test(f))
  it('svg-viewer-C11: no innerHTML, no literal colour, no network address in the component files', () => {
    expect(files.length).toBeGreaterThanOrEqual(4)
    for (const f of files) {
      const t = readFileSync(join(dir, f), 'utf8')
      expect(t, f).not.toMatch(/dangerouslySetInnerHTML|innerHTML|insertAdjacentHTML/)
      expect(t, f).not.toMatch(/#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/)
      expect(t, f).not.toMatch(/localhost|127\.0\.0\.1|https?:\/\//)
    }
  })
})

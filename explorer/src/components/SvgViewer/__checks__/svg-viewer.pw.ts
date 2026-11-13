// Headless browser checks for the picture viewer. Run: npx tsx src/components/SvgViewer/__checks__/svg-viewer.pw.ts
// Needs the dev server on 127.0.0.1:8808 (npx vite --host 127.0.0.1 --port 8808). Writes shots to _captures/svg-viewer/.
import { chromium, type Page } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { join } from 'node:path'
import { chromiumPath } from '../../../../tests/support/chromium'

const BASE = process.env.SVGV_BASE ?? 'http://127.0.0.1:8808'
const H = '/src/components/SvgViewer/__checks__/harness/index.html'
const OUT = join(process.cwd(), '_captures/svg-viewer')
mkdirSync(OUT, { recursive: true })
const results: string[] = []
let failed = 0
const check = (id: string, ok: boolean, detail: string) => { if (!ok) failed++; results.push(`${ok ? 'PASS' : 'FAIL'} ${id}: ${detail}`) }
const scale = async (p: Page) => Number(await p.getByTestId(/svg-viewer$/).first().getAttribute('data-scale'))
const settle = (p: Page) => p.waitForTimeout(500)

/** Share of pixels in the element's screenshot that differ from the page background, decoded in the browser. */
async function inkShare(p: Page, png: Buffer): Promise<number> {
  return p.evaluate(async (b64) => {
    const img = new Image(); img.src = `data:image/png;base64,${b64}`; await img.decode()
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height
    const x = c.getContext('2d')!; x.drawImage(img, 0, 0)
    const d = x.getImageData(0, 0, c.width, c.height).data
    let n = 0
    for (let i = 0; i < d.length; i += 4) if (d[i]! < 235 || d[i + 1]! < 235 || d[i + 2]! < 235) n++
    return n / (d.length / 4)
  }, png.toString('base64'))
}

async function open(browser: Awaited<ReturnType<typeof chromium.launch>>, mode: string, opts: { reduce?: boolean } = {}) {
  const ctx = await browser.newContext({ viewport: { width: 1160, height: 780 }, reducedMotion: opts.reduce ? 'reduce' : 'no-preference' })
  const page = await ctx.newPage()
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()) })
  await page.route(/^https?:\/\/(?!127\.0\.0\.1)/, (r) => r.abort())
  await page.goto(`${BASE}${H}?mode=${mode}`)
  await page.waitForSelector('[data-testid$=".svg-viewer"]')
  return { ctx, page, errors }
}

const browser = await chromium.launch({ headless: true, executablePath: chromiumPath() })
try {
  // C02: a page carrying <script> and onload never runs; four presses read 4.0; the crop is not blank.
  {
    const { ctx, page } = await open(browser, 'hostile')
    await page.waitForSelector('[data-testid$="svg-viewer-image"]')
    await page.waitForTimeout(800) // long enough for any script in the picture to have run
    for (let i = 0; i < 4; i++) await page.getByTestId('electronics.svg-viewer-zoom-in').click()
    await settle(page)
    const pwn = await page.evaluate(() => (window as unknown as { __pwn?: number }).__pwn)
    const s = await scale(page)
    const share = await inkShare(page, await page.getByTestId('electronics.svg-viewer').screenshot({ path: join(OUT, 'hostile-zoom4.png') }))
    const tag = await page.getByTestId('electronics.svg-viewer-image').evaluate((e) => e.tagName)
    check('svg-viewer-C02', pwn === undefined && Math.abs(s - 4) <= 0.05 && share >= 0.02 && tag === 'IMG', `__pwn=${pwn} scale=${s.toFixed(3)} ink=${(share * 100).toFixed(1)}% via <${tag.toLowerCase()}>`)
    await ctx.close()
  }
  // C12 real KiCad page: fit, zoom 4.0 on the page, jump to U5; picture sharp and not blank.
  {
    const { ctx, page, errors } = await open(browser, 'real')
    await page.waitForFunction(() => (document.querySelector('img') as HTMLImageElement | null)?.naturalWidth! > 0)
    await settle(page)
    const fit = await page.getByTestId('electronics.svg-viewer').screenshot({ path: join(OUT, 'real-fit.png') })
    check('svg-viewer-C12', (await inkShare(page, fit)) >= 0.02 && (await scale(page)) === 1, `fit ink=${((await inkShare(page, fit)) * 100).toFixed(1)}%`)
    // drag pans the picture by the mouse travel
    const img = page.getByTestId('electronics.svg-viewer-image')
    const b0 = (await img.boundingBox())!
    await page.mouse.move(500, 300); await page.mouse.down(); await page.mouse.move(560, 340, { steps: 4 }); await page.mouse.up()
    const b1 = (await img.boundingBox())!
    check('svg-viewer-C13', Math.abs(b1.x - b0.x - 60) < 2 && Math.abs(b1.y - b0.y - 40) < 2, `dragged by (${(b1.x - b0.x).toFixed(1)}, ${(b1.y - b0.y).toFixed(1)}) for a 60,40 drag`)
    // wheel zooms
    await page.mouse.move(500, 300); await page.mouse.wheel(0, -400); await settle(page)
    const sw = await scale(page)
    check('svg-viewer-C14', sw > 1.5, `wheel -400 gave scale ${sw.toFixed(2)}`)
    await page.getByTestId('electronics.svg-viewer-fit').click(); await settle(page)
    check('svg-viewer-C15', (await scale(page)) === 1 && Math.abs((await img.boundingBox())!.x - b0.x) < 2, 'Fit returns to scale 1 and the first position')
    // keyboard
    await page.getByRole('group', { name: /Microphones/ }).focus()
    for (let i = 0; i < 4; i++) await page.keyboard.press('+')
    await settle(page)
    check('svg-viewer-C16', Math.abs((await scale(page)) - 4) < 0.05, `4 x "+" gave ${(await scale(page)).toFixed(3)}`)
    await page.keyboard.press('0'); await settle(page)
    check('svg-viewer-C17', (await scale(page)) === 1, '"0" fits')
    check('svg-viewer-C18', errors.length === 0, `console errors: ${errors.length} ${errors[0] ?? ''}`)
    await ctx.close()
  }
  {
    const { ctx, page } = await open(browser, 'real-u5')
    await page.waitForFunction(() => (document.querySelector('img') as HTMLImageElement | null)?.naturalWidth! > 0)
    await settle(page)
    const s = await scale(page)
    const shot = await page.getByTestId('electronics.svg-viewer').screenshot({ path: join(OUT, 'real-u5.png') })
    const f = (await page.getByTestId('electronics.svg-viewer-focus').boundingBox())!
    const v = (await page.getByTestId('electronics.svg-viewer').boundingBox())!
    const dx = Math.abs(f.x + f.width / 2 - (v.x + v.width / 2)), dy = Math.abs(f.y + f.height / 2 - (v.y + v.height / 2))
    check('svg-viewer-C19', s > 2 && dx < 3 && dy < 3 && (await inkShare(page, shot)) >= 0.02, `jump to U5: scale ${s.toFixed(2)}, centre off by (${dx.toFixed(1)}, ${dy.toFixed(1)}) px, ink ${((await inkShare(page, shot)) * 100).toFixed(1)}%`)
    await ctx.close()
  }
  // C20 missing and broken pictures say so in words
  for (const [mode, words] of [['missing', 'Not built yet. Run npm run collect.'], ['broken', 'cannot be read: not-there.svg']] as const) {
    const { ctx, page } = await open(browser, mode)
    await page.waitForSelector('[data-testid="board.state-banner"]')
    const t = (await page.getByTestId('board.state-banner').textContent()) ?? ''
    await page.getByTestId('board.svg-viewer').screenshot({ path: join(OUT, `${mode}.png`) })
    check(`svg-viewer-C20-${mode}`, t.includes(words) && (await page.getByTestId('board.svg-viewer-image').count()) === 0, `"${t}"`)
    await ctx.close()
  }
  // C21 reduced motion: the layer carries no easing
  for (const reduce of [false, true]) {
    const { ctx, page } = await open(browser, 'small', { reduce })
    const d = await page.locator('.svgv-layer').evaluate((e) => getComputedStyle(e).transitionDuration)
    const secs = Math.max(...d.split(',').map((x) => parseFloat(x)))
    check(`svg-viewer-C21-${reduce ? 'reduced' : 'normal'}`, reduce ? secs <= 0.001 : secs >= 0.2, `transition-duration ${d}`)
    await ctx.close()
  }
} catch (e) {
  check('svg-viewer-run', false, `the run stopped: ${String(e).split('\n')[0]}`)
} finally {
  await browser.close()
}
console.log(results.join('\n'))
console.log(`svg-viewer pw: ${results.length - failed}/${results.length} passed`)
process.exit(failed ? 1 : 0)

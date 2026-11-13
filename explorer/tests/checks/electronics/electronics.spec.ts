// electronics-C01..C08: the Electronics screen on the LIVE bundle, on a made-up RICH bundle (7 blocks, 8 pages,
// both tables), on a bundle whose wiring pictures are missing, and on an EMPTY one. Headless; 127.0.0.1 only.
// Each bundle gets its own app (live 8840, rich 8841, no pictures 8842, empty 8843); a check stops only what it started.
// Every expected value is read from the bundle on disk; none is written here.
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import type { Electronics, Manifest, SchematicPages } from '../../../src/contract/records'
import { EXPLORER_ROOT, bundleEnv, byTestId, emptyBundle, startApp, watchConsole, type RunningApp } from '../../support'
import { makeRichBundle } from './rich-bundle'

const LIVE = join(EXPLORER_ROOT, 'public', 'data')
const tmp = mkdtempSync(join(tmpdir(), 'el-checks-'))
const RICH = makeRichBundle(join(tmp, 'rich'))
const NOPIC = makeRichBundle(join(tmp, 'nopic'), { schematic: false })
const GONE = makeRichBundle(join(tmp, 'gone'))
{
  // the pictures record is missing from this one: no file, and the manifest says so
  rmSync(join(GONE, 'schematic'), { recursive: true, force: true })
  const m = JSON.parse(readFileSync(join(GONE, 'manifest.json'), 'utf8')) as Manifest
  m.records['schematic-pages'] = { ...m.records['schematic-pages'], status: 'missing', message: 'made up' }
  writeFileSync(join(GONE, 'manifest.json'), JSON.stringify(m))
}
const read = <T>(dir: string, f: string): T => JSON.parse(readFileSync(join(dir, f), 'utf8')) as T

const apps: Record<string, RunningApp> = {}
test.beforeAll(async () => {
  apps.live = await startApp({ port: 8840, env: bundleEnv(LIVE) })
  apps.rich = await startApp({ port: 8841, env: bundleEnv(RICH) })
  apps.nopic = await startApp({ port: 8842, env: bundleEnv(GONE) })
  apps.empty = await startApp({ port: 8843, env: bundleEnv(emptyBundle()) })
})
test.afterAll(async () => {
  for (const a of Object.values(apps)) await a?.stop()
  rmSync(tmp, { recursive: true, force: true })
})

const open = async (page: Page, app: RunningApp, search = '') => {
  await page.goto(`${app.url}/electronics${search}`)
  await page.waitForSelector('[data-testid="electronics.panel"]', { timeout: 100_000 })
}
const BUNDLES = [['live', LIVE], ['rich', RICH]] as const
const noise = (errs: string[]) => errs.filter((e) => !/Failed to load resource.*404/.test(e) && !/http 404: .*\/data\//.test(e))

for (const [name, dir] of BUNDLES) {
  const el = read<Electronics>(dir, 'electronics.json')
  const pages = read<SchematicPages>(dir, 'schematic/index.json').pages

  test(`electronics-C01 [${name}] blocks, pin plan rows and power budget equal the bundle`, async ({ page }) => {
    await open(page, apps[name]!)
    await expect(byTestId(page, 'electronics', 'block')).toHaveCount(el.blocks.length)
    for (const b of el.blocks) await expect(page.locator(`[data-testid="electronics.block"][data-block="${b.id}"]`)).toContainText(b.label)
    await byTestId(page, 'electronics', 'tab-pins').click()
    await expect(byTestId(page, 'electronics', 'pin-row')).toHaveCount(el.pin_plan.rows.length)
    await byTestId(page, 'electronics', 'tab-power').click()
    const rows = byTestId(page, 'electronics', 'power-row')
    await expect(rows).toHaveCount(el.power_budget.rows.length)
    for (const [i, r] of el.power_budget.rows.entries()) await expect(rows.nth(i)).toContainText(r[0] ?? '')
  })

  test(`electronics-C02 [${name}] a block opens its page within 1 s; the page is not blank; the panel expands and Escape closes it`, async ({ page }) => {
    await open(page, apps[name]!)
    const b = el.blocks[1]!
    const pg = pages.find((p) => p.id === b.sheet || p.id === b.id)!
    await page.locator(`[data-testid="electronics.block"][data-block="${b.id}"]`).click()
    const img = byTestId(page, 'electronics', 'svg-viewer-image')
    await expect(img).toHaveAttribute('src', new RegExp(`${pg.svg!.replace(/[/.]/g, '\\$&')}$`), { timeout: 1000 })
    await expect.poll(() => img.evaluate((i: HTMLImageElement) => i.naturalWidth), { timeout: 1000 }).toBeGreaterThan(0)
    const share = await page.screenshot({ clip: (await byTestId(page, 'electronics', 'svg-viewer').boundingBox())! }).then((buf) =>
      page.evaluate(async (b64) => {
        const bm = await createImageBitmap(await (await fetch('data:image/png;base64,' + b64)).blob())
        const c = new OffscreenCanvas(bm.width, bm.height)
        const x = c.getContext('2d')!
        x.drawImage(bm, 0, 0)
        const d = x.getImageData(0, 0, bm.width, bm.height).data
        let n = 0
        for (let i = 0; i < d.length; i += 4) if ((d[i] ?? 255) < 235 || (d[i + 1] ?? 255) < 235 || (d[i + 2] ?? 255) < 235) n++
        return n / (d.length / 4)
      }, buf.toString('base64')),
    )
    expect(share).toBeGreaterThan(0.02)
    const main = page.locator('main.main')
    const mw = (await main.boundingBox())!.width
    // the screen opens the panel wide by itself; Escape closes it, the control opens it again
    await expect.poll(async () => (await byTestId(page, 'app', 'panel').boundingBox())!.width, { timeout: 20_000 }).toBeGreaterThan(mw * 0.9)
    await page.keyboard.press('Escape')
    await expect.poll(async () => (await byTestId(page, 'app', 'panel').boundingBox())!.width / mw, { timeout: 20_000 }).toBeLessThan(0.45)
    await byTestId(page, 'app', 'panel-expand').click()
    await expect.poll(async () => (await byTestId(page, 'app', 'panel').boundingBox())!.width, { timeout: 20_000 }).toBeGreaterThan(mw * 0.9)
  })

  test(`electronics-C03 [${name}] "Parts of this page" goes to Parts with that page; the part rows equal the page's parts`, async ({ page }) => {
    await open(page, apps[name]!)
    const b = el.blocks[1]!
    const pg = pages.find((p) => p.id === b.sheet || p.id === b.id)!
    await page.locator(`[data-testid="electronics.block"][data-block="${b.id}"]`).click()
    const ids = new Set([...pg.part_ids, ...b.part_ids])
    await expect(byTestId(page, 'electronics', 'part-row')).toHaveCount(ids.size)
    await byTestId(page, 'electronics', 'parts-of-page').click()
    await expect.poll(() => new URL(page.url()).pathname).toBe('/parts')
    expect(new URL(page.url()).searchParams.get('page')).toBe(pg.id)
  })

  test(`electronics-C06 [${name}] a part row selects the part: ?part= is set, its card opens, a reload keeps block and part`, async ({ page }) => {
    await open(page, apps[name]!)
    const b = el.blocks[1]!
    await page.locator(`[data-testid="electronics.block"][data-block="${b.id}"]`).click()
    const id = b.part_ids[0]!
    await page.locator(`[data-testid="electronics.part-row"][data-part="${id}"]`).click()
    await expect(page.locator(`[data-testid="electronics.part-card"][data-part-id="${id}"]`)).toBeVisible()
    expect(new URL(page.url()).searchParams.get('part')).toBe(id)
    await page.reload()
    await page.waitForSelector('[data-testid="electronics.block"]', { timeout: 100_000 })
    await expect(page.locator(`[data-testid="electronics.part-card"][data-part-id="${id}"]`)).toBeVisible()
    await expect(page.locator(`[data-testid="electronics.block"][data-block="${b.id}"]`)).toHaveAttribute('aria-pressed', 'true')
  })

  test(`electronics-C07 [${name}] no page scroll at 1512x982, 1440x900 and 1280x800`, async ({ page }) => {
    for (const [w, h] of [[1512, 982], [1440, 900], [1280, 800]] as const) {
      await page.setViewportSize({ width: w, height: h })
      await open(page, apps[name]!)
      expect(await page.evaluate(() => document.scrollingElement!.scrollHeight <= innerHeight)).toBe(true)
      expect(await page.evaluate(() => { const b = document.querySelector('[data-testid="app.panel-body"]')!; return b.scrollWidth <= b.clientWidth + 1 })).toBe(true)
    }
  })

  test(`electronics-C08 [${name}] the pin plan find box keeps the rows that contain the text`, async ({ page }) => {
    await open(page, apps[name]!, '?tab=pins')
    const word = el.pin_plan.rows[el.pin_plan.rows.length - 1]![0]!
    await byTestId(page, 'electronics', 'table-find').fill(word)
    const want = el.pin_plan.rows.filter((r) => r.some((c) => c.toLowerCase().includes(word.toLowerCase()))).length
    await expect(byTestId(page, 'electronics', 'pin-row')).toHaveCount(want)
  })
}

test('electronics-C09 [live] at 1440x900 the picture is at least 900 px wide and fills the height; a part row jumps the picture to it', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await open(page, apps.live!)
  await expect.poll(async () => (await byTestId(page, 'electronics', 'svg-viewer').boundingBox())!.width, { timeout: 20_000 }).toBeGreaterThanOrEqual(900)
  await expect.poll(async () => (await byTestId(page, 'electronics', 'svg-viewer').boundingBox())!.height, { timeout: 20_000 }).toBeGreaterThanOrEqual(900 - 56 - 330)
  const el = read<Electronics>(LIVE, 'electronics.json')
  const pages = read<SchematicPages>(LIVE, 'schematic/index.json').pages
  const b = el.blocks.find((x) => x.id === 'main') ?? el.blocks[0]!
  const pg = pages.find((p) => p.id === b.sheet)!
  const svg = readFileSync(join(LIVE, pg.svg!), 'utf8')
  const id = b.part_ids.find((i) => new RegExp(`<text\\s+x="[\\d.-]+"\\s+y="[\\d.-]+"[^>]*>${i.split(':')[1]}</text>`).test(svg))!
  await page.locator(`[data-testid="electronics.block"][data-block="${b.id}"]`).click()
  await page.locator(`[data-testid="electronics.part-row"][data-part="${id}"]`).click()
  await expect(byTestId(page, 'electronics', 'svg-viewer-focus')).toBeVisible({ timeout: 10_000 })
  await expect.poll(async () => Number((await byTestId(page, 'electronics', 'svg-viewer-scale').innerText()).replace(/[^\d.]/g, ''))).toBeGreaterThan(150)
})

test('electronics-C04 pictures missing: the blocks stay, and a PDF link with words shows', async ({ page }) => {
  await open(page, apps.nopic!)
  const el = read<Electronics>(GONE, 'electronics.json')
  await expect(byTestId(page, 'electronics', 'block')).toHaveCount(el.blocks.length)
  await expect(byTestId(page, 'electronics', 'state-banner').first()).toBeVisible()
  const link = byTestId(page, 'electronics', 'pdf-link')
  await expect(link).toBeVisible()
  await expect(link).toContainText('PDF')
  await expect(byTestId(page, 'electronics', 'pdf-fallback')).toContainText('not built yet')
})

test('electronics-C05 empty bundle: one banner with the command in <code>, no blocks, 0 console errors', async ({ page }) => {
  const w = watchConsole(page)
  await open(page, apps.empty!)
  const banner = byTestId(page, 'app', 'panel').getByTestId('electronics.state-banner')
  await expect(banner).toHaveCount(1)
  await expect(banner.locator('code')).toHaveText('npm run collect')
  await expect(byTestId(page, 'electronics', 'block')).toHaveCount(0)
  expect((await byTestId(page, 'electronics', 'panel').innerText()).trim().length).toBeGreaterThan(20)
  expect(noise(w.errors)).toEqual([])
})

// home-C01..C07: the Home screen, on the LIVE bundle and on an EMPTY one. Headless; 127.0.0.1 only.
// Each check starts its own app (live on 8804, empty on 8806) and stops only what it started.
// Values are read from the bundle on disk; none is written here.
import { cpSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { expect, test, type Page } from '@playwright/test'
import { AREA_PILL } from '../../../src/contract/vocabulary'
import type { AreaStates, KeyNumbers, Manifest } from '../../../src/contract/records'
import { EXPLORER_ROOT, SAMPLE_BUNDLE, bundleEnv, byTestId, emptyBundle, startApp, waitStageReady, watchConsole, type RunningApp } from '../../support'

const LIVE = join(EXPLORER_ROOT, 'public', 'data')
const read = <T>(f: string): T => JSON.parse(readFileSync(join(LIVE, f), 'utf8')) as T
const facts = read<KeyNumbers>('facts.json')
const areas = read<AreaStates>('areas.json')
const manifest = read<Manifest>('manifest.json')
const liveStatus = read<{ exterior: { status: string } }>('ring-model.json').exterior.status
const bannerKey = (st: string) => (st === 'in-design' ? 'exterior-in-design' : st === 'not-picked' ? 'exterior-not-picked' : 'none')
const PATH = (id: string) => (id === 'home' ? '/' : `/${id}`)

let live: RunningApp
let empty: RunningApp
test.beforeAll(async () => {
  live = await startApp({ port: 8804, env: bundleEnv(LIVE) })
  empty = await startApp({ port: 8806, env: bundleEnv(emptyBundle()) })
})
test.afterAll(async () => {
  await live?.stop()
  await empty?.stop()
})

const open = async (page: Page, app: RunningApp) => {
  await page.goto(app.url + '/')
  await page.waitForSelector('[data-testid="home.panel"]')
}

test('home-C01 each key number on screen equals the bundle value', async ({ page }) => {
  await open(page, live)
  const rows = byTestId(page, 'home', 'key-number')
  await expect(rows.filter({ hasNot: page.locator('[data-left-out]') }).first()).toBeVisible()
  for (const f of facts.facts) {
    const row = page.locator(`[data-testid="home.key-number"][data-fact="${f.id}"]`)
    await expect(row).toContainText(f.label)
    await expect(row.locator('.kn-value')).toContainText(String(f.value))
  }
})

test('home-C02 8 tiles, each with one pill equal to areas.json, each leading to its route', async ({ page }) => {
  await open(page, live)
  const tiles = byTestId(page, 'home', 'area-tile')
  await expect(tiles).toHaveCount(8)
  for (const a of areas.areas) {
    const tile = page.locator(`[data-testid="home.area-tile"][data-area="${a.id}"]`)
    await expect(tile.getByTestId('home.state-pill')).toHaveCount(1)
    await expect(tile.getByTestId('home.state-pill')).toHaveText(AREA_PILL[a.state])
  }
  for (const a of areas.areas) {
    await open(page, live)
    await page.locator(`[data-testid="home.area-tile"][data-area="${a.id}"]`).click()
    await expect.poll(() => new URL(page.url()).pathname).toBe(PATH(a.id))
  }
})

test('home-C03 empty bundle: one banner with the command in <code>, 0 console errors, no tiles', async ({ page }) => {
  const w = watchConsole(page)
  await open(page, empty)
  // the stage draws its own banner (also `home.state-banner`) in the stage area: count the panel's only
  const banner = byTestId(page, 'app', 'panel').getByTestId('home.state-banner')
  await expect(banner).toHaveCount(1)
  await expect(banner.locator('code')).toHaveText('npm run collect')
  await expect(byTestId(page, 'home', 'area-tile')).toHaveCount(0)
  const real = w.errors.filter((e) => !/http 404: .*\/data\//.test(e) && !/Failed to load resource.*404/.test(e))
  expect(real).toEqual([])
})

const nonBlankShare = (page: Page, clip: { x: number; y: number; width: number; height: number }) =>
  page.screenshot({ clip }).then((buf) =>
    page.evaluate(async (b64) => {
      const img = await createImageBitmap(await (await fetch('data:image/png;base64,' + b64)).blob())
      const c = new OffscreenCanvas(img.width, img.height)
      const g = c.getContext('2d')!
      g.drawImage(img, 0, 0)
      const d = g.getImageData(0, 0, img.width, img.height).data
      let n = 0
      for (let i = 0; i < d.length; i += 4) if (d[i]! < 235 || d[i + 1]! < 235 || d[i + 2]! < 235) n++
      return n / (d.length / 4)
    }, buf.toString('base64')),
  )

test('home-C04 slab label, ring drawn and moving, no page scroll at 1512x982 and 1280x800', async ({ page }) => {
  for (const [w, h] of [[1512, 982], [1280, 800]] as const) {
    await page.setViewportSize({ width: w, height: h })
    await open(page, live)
    await waitStageReady(page)
    await expect(byTestId(page, 'app', 'panel').locator(`[data-kind="${bannerKey(liveStatus)}"]`)).toHaveCount(liveStatus === 'in-design' || liveStatus === 'not-picked' ? 1 : 0)
    const scroll = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)
    expect(scroll).toBeLessThanOrEqual(0)
  }
  await page.setViewportSize({ width: 1512, height: 982 })
  await open(page, live)
  await waitStageReady(page)
  const box = (await byTestId(page, 'app', 'stage').boundingBox())!
  const clip = { x: box.x + 20, y: box.y + 20, width: box.width - 40, height: box.height - 40 }
  expect(await nonBlankShare(page, clip)).toBeGreaterThan(0.02)
  expect(await page.evaluate(() => window.__stage?.autoRotate)).toBe(true)
  const before = await page.screenshot({ clip })
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2)
  await page.mouse.down()
  await page.mouse.move(box.x + box.width / 2 + 160, box.y + box.height / 2 + 20, { steps: 12 })
  await page.mouse.up()
  await page.waitForTimeout(400)
  expect((await page.screenshot({ clip })).equals(before)).toBe(false)
})

test('home-C05 the source of a key number appears on hover and opens its file', async ({ page }) => {
  await open(page, live)
  const f = facts.facts[0]!
  const row = page.locator(`[data-testid="home.key-number"][data-fact="${f.id}"]`)
  const src = row.locator('.kn-source')
  await expect(src).toHaveCSS('opacity', '0')
  await row.hover()
  await expect(src).toHaveCSS('opacity', '1')
  await expect(src).toContainText(f.source.file)
  const href = await row.getByTestId('home.key-source').getAttribute('href')
  expect(href).toBe('/files/' + f.source.file)
  const res = await page.request.get(live.url + href!)
  expect(res.status()).toBe(200)
})

test('home-C06 a fact the collector left out reads "not known yet", never a number', async ({ page }) => {
  await open(page, live)
  const message = manifest.records['key-numbers'].message ?? ''
  const name = /^Left out, not readable: ([^:]+):/.exec(message)?.[1]
  test.skip(!name, 'this bundle left nothing out')
  const row = page.locator(`[data-testid="home.key-number"][data-left-out="true"]`)
  await expect(row).toHaveCount(1)
  await expect(row.locator('.kn-value')).toHaveText('not known yet for this ring')
  await expect(row.locator('.kn-source')).toContainText(message.split(': ').slice(2).join(': ').slice(0, 30))
})

test('home-C07 what is next for the owner lists the areas whose "who" is the owner', async ({ page }) => {
  await open(page, live)
  const mine = areas.areas.filter((a) => a.who === 'owner' && a.state !== 'done')
  test.skip(mine.length === 0, 'no area waits on the owner in this bundle')
  const items = byTestId(page, 'home', 'next-item')
  await expect(items).toHaveCount(Math.min(mine.length, 4))
  await expect(items.first()).toContainText(mine[0]!.why ?? '')
})

for (const status of ['picked', 'in-design', 'not-picked'] as const) {
  test(`home-C08 exterior status ${status} (made-up bundle) shows the banner ${bannerKey(status)}`, async ({ page }) => {
    const dir = mkdtempSync(join(tmpdir(), 'home-c08-'))
    cpSync(SAMPLE_BUNDLE, dir, { recursive: true })
    const f = join(dir, 'ring-model.json')
    const m = JSON.parse(readFileSync(f, 'utf8'))
    m.exterior.status = status
    writeFileSync(f, JSON.stringify(m))
    const app = await startApp({ port: 8808, env: bundleEnv(dir) })
    try {
      await open(page, app)
      const kinds = page.locator('[data-testid="app.panel"] [data-kind^="exterior"]')
      await expect(page.getByTestId('home.area-tile').first()).toBeVisible({ timeout: 20_000 })
      if (status === 'picked') await expect(kinds).toHaveCount(0)
      else {
        await expect(kinds).toHaveCount(1)
        await expect(kinds).toHaveAttribute('data-kind', bannerKey(status))
      }
    } finally {
      await app.stop()
      await new Promise((r) => setTimeout(r, 1500))
    }
  })
}

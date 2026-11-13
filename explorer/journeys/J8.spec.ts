// J8: Download the maker files of the metal body for a 3D printer or a maker (the owner's ask: "ability to
// download [files] for a 3D printer"). Not a signed journey: a request of the owner after sign-off.
// Reached as a user would: Home, tile Inside, layer row Body, the body part. Expected values come from the
// bundle (parts.json) and the design files on disk (EXPLORER_SOURCE). Headless only.
// Ids on the page: inside.part-card (data-part-id, data-made), inside.file-button (data-file = drawing | spec | step | stl),
// inside.size-switch with its buttons (data-size), inside.layer-row (data-layer), inside.layer-part (data-part-id).
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { expect as baseExpect, test, type Locator, type Page } from '@playwright/test'
import { FIXTURE_DATA, FIXTURE_SOURCE, blockOffline, byTestId, watchConsole } from '../tests/support'

const expect = baseExpect.configure({ timeout: 15_000 })
test.describe.configure({ timeout: 90_000 })

const J8_1 = "J8#1"

const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
const SOURCE = process.env.EXPLORER_SOURCE ?? FIXTURE_SOURCE
const BODY_ID = 'ring:HSG1'
const BODY_DIR = 'design/mfg/parts/body'
/** The file the first download is compared with (default size 9). */
const FIRST_STL = 'body-us9.stl'
/** The disk file the first download is compared with; only a red-first run changes it (J8_DISK_STL=body-us7.stl). */
const DISK_STL = process.env.J8_DISK_STL ?? FIRST_STL

function bundleRecord<T>(file: string): T {
  if (!existsSync(join(BUNDLE, 'manifest.json'))) throw new Error(`journey setup: no bundle at ${BUNDLE}; set EXPLORER_BUNDLE`)
  return JSON.parse(readFileSync(join(BUNDLE, file), 'utf8')) as T
}
const disk = (name: string): Buffer => {
  const p = join(SOURCE, BODY_DIR, name)
  if (!existsSync(p)) throw new Error(`journey setup: ${p} is not on disk; set EXPLORER_SOURCE to the folder that holds design/`)
  return readFileSync(p)
}
const sha = (b: Buffer) => createHash('sha256').update(b).digest('hex')

const file = (page: Page, kind: string): Locator => byTestId(page, 'inside', 'file-button').and(page.locator(`[data-file="${kind}"]`))

async function download(page: Page, link: Locator): Promise<Buffer> {
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 30_000 }), link.click()])
  return readFileSync((await dl.path())!)
}

test(`${J8_1} (J8.1) Inside: the metal body offers drawing, specification, STEP and STL; the STL is the file on disk, per ring size`, async ({ page }) => {
  const w = watchConsole(page)
  await blockOffline(page, w)
  const line = bundleRecord<{ lines: { part_ids: string[]; item: string }[] }>('parts.json').lines.find((l) => l.part_ids.includes(BODY_ID))
  expect(line, `control: no parts-list line for ${BODY_ID} in the bundle`).toBeTruthy()

  // arrive as a user: Home, tile Inside, layer row Body, the body part
  await page.goto('/')
  const tile = byTestId(page, 'home', 'area-tile').and(page.locator('[data-area="inside"]'))
  await expect(tile, 'Home has no Inside tile').toBeVisible()
  await tile.click()
  const row = byTestId(page, 'inside', 'layer-row').and(page.locator('[data-layer="body"]'))
  await expect(row, 'Inside has no layer row "body" (inside.layer-row[data-layer=body])').toBeVisible()
  await row.click()
  const part = byTestId(page, 'inside', 'layer-part').and(page.locator(`[data-part-id="${BODY_ID}"]`))
  await expect(part.first(), `the Body layer lists no object for ${BODY_ID}`).toBeVisible()
  await part.first().click()

  const card = byTestId(page, 'inside', 'part-card')
  await expect(card, 'no part card for the body').toHaveAttribute('data-part-id', BODY_ID)
  await expect(card).toContainText(line!.item)

  // four links, present and enabled
  for (const kind of ['drawing', 'spec', 'step', 'stl']) {
    const l = file(page, kind)
    await expect(l, `no '${kind}' file button (inside.file-button[data-file=${kind}])`).toHaveCount(1)
    await expect(l, `the '${kind}' link is greyed`).not.toHaveAttribute('aria-disabled', 'true')
    await expect(l, `the '${kind}' control is not a link with an address`).toHaveAttribute('href', /\S/)
  }

  // STL at the default size equals the file on disk
  await expect(file(page, 'stl')).toHaveAttribute('href', new RegExp(`${FIRST_STL.replace('.', '\\.')}$`))
  const first = await download(page, file(page, 'stl'))
  expect(first.length, 'the downloaded STL is empty').toBeGreaterThan(0)
  expect(sha(first), `the downloaded STL differs from ${BODY_DIR}/${DISK_STL} on disk`).toBe(sha(disk(DISK_STL)))

  // ring size 12: the link and the bytes follow
  const size = byTestId(page, 'inside', 'size-switch').locator('[data-size="12"]')
  await expect(size, 'no ring size 12 in the size switch (inside.size-switch)').toBeVisible()
  await size.click()
  await expect(file(page, 'stl')).toHaveAttribute('href', /body-us12\.stl$/)
  const twelve = await download(page, file(page, 'stl'))
  expect(sha(twelve), 'the STL of size 12 differs from body-us12.stl on disk').toBe(sha(disk('body-us12.stl')))
  expect(sha(twelve), 'size 12 and the default size give the same file').not.toBe(sha(first))

  // the drawing PDF answers 200 with a pdf content type
  const href = await file(page, 'drawing').getAttribute('href')
  const res = await page.request.get(new URL(href!, page.url()).toString())
  expect(res.status(), `the drawing answers ${res.status()}`).toBe(200)
  expect(res.headers()['content-type'] ?? '', 'the drawing is not served as a pdf').toMatch(/pdf/i)
  expect((await res.body()).subarray(0, 4).toString('latin1'), 'the drawing body is not a PDF').toBe('%PDF')
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

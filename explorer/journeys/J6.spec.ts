// J6: Hand the design to a build partner (docs/JOURNEYS.md J6.1 and J6.2; rows J6#1 and J6#2 of docs/TEST-PLAN.md section 3).
// Written from the signed journey table, never from a built screen. Every expected value is read from the
// bundle under test (EXPLORER_BUNDLE) and the design files (EXPLORER_SOURCE). Headless only.
// Element ids follow docs/CONTRACT.md section 6; the ids this file needs are listed in docs/lanes/journeys-a.md.
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { expect as baseExpect, test, type Page } from '@playwright/test'
import { FIXTURE_DATA, FIXTURE_SOURCE, blockOffline, byTestId, watchConsole } from '../tests/support'

const expect = baseExpect.configure({ timeout: 6_000 })
test.describe.configure({ timeout: 60_000 })

const J6_1 = "J6#1"
const J6_2 = "J6#2"

const BUNDLE = process.env.EXPLORER_BUNDLE ?? FIXTURE_DATA
const SOURCE = process.env.EXPLORER_SOURCE ?? FIXTURE_SOURCE
function bundleRecord<T>(file: string): T {
  if (!existsSync(join(BUNDLE, 'manifest.json'))) {
    throw new Error(`journey setup: no bundle at ${BUNDLE} (manifest.json missing). Set EXPLORER_BUNDLE to a built bundle folder: the frozen copy .cache/fixture-99dfb85/data, or public/data after npm run collect.`)
  }
  const p = join(BUNDLE, file)
  if (!existsSync(p)) throw new Error(`journey setup: record ${file} is missing from the bundle ${BUNDLE}; the bundle is not complete for this journey`)
  return JSON.parse(readFileSync(p, 'utf8')) as T
}
function sourceFile(rel: string): string {
  const p = join(SOURCE, rel)
  if (!existsSync(p)) throw new Error(`journey setup: design file ${rel} is not under EXPLORER_SOURCE (${SOURCE}); set EXPLORER_SOURCE to the folder that holds design/`)
  return p
}
const sha256 = (b: Buffer) => createHash('sha256').update(b).digest('hex')

/** Minimal RFC 4180 reader, independent of the app: quoted cells, doubled quotes, commas and line breaks inside quotes. */
function parseCsv(text: string): string[][] {
  const rows: string[][] = []
  let row: string[] = []
  let cell = ''
  let q = false
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]!
    if (q) {
      if (ch === '"') {
        if (text[i + 1] === '"') (cell += '"', i++)
        else q = false
      } else cell += ch
    } else if (ch === '"') q = true
    else if (ch === ',') (row.push(cell), (cell = ''))
    else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++
      row.push(cell)
      cell = ''
      rows.push(row)
      row = []
    } else cell += ch
  }
  if (cell !== '' || row.length) (row.push(cell), rows.push(row))
  return rows.filter((r) => r.some((c) => c !== ''))
}

/** Click a tab of the top bar; an absent tab fails at once and says so. */
async function clickTab(page: Page, id: string): Promise<void> {
  const t = byTestId(page, 'app', `tab-${id}`)
  await expect(t, `the top bar has no entry '${id}' (app.tab-${id})`).toBeVisible()
  await t.click()
}

interface FileRow { path: string; size_bytes: number; modified: string; area: string }
interface Files { files: FileRow[]; bundle: { file: string; size_bytes: number; contents: string[] } | null }

test(`${J6_1} (J6.1) Files: "Download partner bundle" delivers a complete zip and the page lists what it holds`, async ({ page }) => {
  const w = watchConsole(page)
  await blockOffline(page, w)
  await page.goto('/')
  await clickTab(page, 'files')
  await expect(page, 'the top bar "Files" did not go to the files section of /open').toHaveURL(/\/open(\/|\?)?#files$/)

  // sees: every file grouped by area with size and date
  const files = bundleRecord<Files>('files.json')
  const byArea = new Map<string, FileRow[]>()
  for (const f of files.files) byArea.set(f.area, [...(byArea.get(f.area) ?? []), f])
  const groups = byTestId(page, 'open', 'file-group')
  await expect(groups, 'no file groups on the Files section (open.file-group)').toHaveCount(byArea.size)
  for (const [area, rows] of byArea) {
    const g = groups.and(page.locator(`[data-area="${area}"]`))
    await expect(g, `no group for area '${area}'`).toHaveCount(1)
    await expect(g.locator('[data-testid="open.file-row"]'), `group '${area}' lists the wrong number of files`).toHaveCount(rows.length)
  }
  const first = byTestId(page, 'open', 'file-row').first()
  await expect(first.locator('[data-testid="open.file-size"]')).not.toHaveText('')
  await expect(first.locator('[data-testid="open.file-date"]')).not.toHaveText('')

  // does: clicks "Download partner bundle"
  expect(files.bundle, 'control: files.json lists no partner bundle').not.toBeNull()
  const bundle = files.bundle!
  const button = byTestId(page, 'open', 'download-bundle')
  await expect(button, 'no "Download partner bundle" control (open.download-bundle)').toBeVisible()
  await expect(button).toBeEnabled()
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 20_000 }), button.click()])
  expect(dl.suggestedFilename()).toMatch(/\.zip$/)
  const saved = await dl.path()
  const bytes = readFileSync(saved)
  expect(bytes.length, 'the downloaded size differs from the bundle size in files.json').toBe(bundle.size_bytes)
  expect(statSync(join(BUNDLE, bundle.file.split('/').pop()!)).size).toBe(bundle.size_bytes)
  expect(bytes.subarray(0, 2).toString('latin1'), 'the download is not a zip (no PK header): an error page saved as zip?').toBe('PK')
  expect(() => execFileSync('unzip', ['-tq', saved], { stdio: 'pipe' }), 'unzip -t reports a damaged archive').not.toThrow()

  // the zip holds what the page lists, and a file with a plus sign in its name arrives with the right bytes
  const listing = execFileSync('unzip', ['-Z1', saved], { maxBuffer: 64 * 1024 * 1024 }).toString().split('\n').filter(Boolean)
  expect(listing.length, 'the zip holds a different number of entries than files.json says').toBe(bundle.contents.length)
  await expect(byTestId(page, 'open', 'bundle-entry'), 'the page does not list what the zip contains (open.bundle-entry)').toHaveCount(listing.length)
  const plus = bundle.contents.find((p) => p.includes('+'))
  expect(plus, 'control: no file with a plus sign in its name in the partner bundle').toBeTruthy()
  expect(listing).toContain(plus!)
  const inZip = execFileSync('unzip', ['-p', saved, plus!], { maxBuffer: 64 * 1024 * 1024 })
  expect(sha256(inZip), `bytes of ${plus} in the zip differ from the design file`).toBe(sha256(readFileSync(sourceFile(plus!))))
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

test(`${J6_2} (J6.2) Parts: "Export CSV" downloads bom.csv equal to the source file`, async ({ page }) => {
  const w = watchConsole(page)
  await blockOffline(page, w)
  await page.goto('/')
  await clickTab(page, 'parts')
  await expect(page, 'the top bar "Parts" did not go to /parts').toHaveURL(/\/parts(\/|\?|#|$)/)

  const totals = bundleRecord<{ totals: { ring: { lines: number; parts: number } } }>('parts.json').totals.ring
  const t = byTestId(page, 'parts', 'totals')
  await expect(t, 'the Parts screen shows no totals (parts.totals)').toBeVisible()
  await expect(t).toContainText(`${totals.lines} lines`)
  await expect(t).toContainText(`${totals.parts} parts`)

  const button = byTestId(page, 'parts', 'export-csv')
  await expect(button, 'no "Export CSV" control (parts.export-csv)').toBeVisible()
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 20_000 }), button.click()])
  expect(dl.suggestedFilename()).toBe('bom.csv')
  const got = readFileSync((await dl.path())!)
  const want = readFileSync(sourceFile('design/bom.csv'))
  expect(sha256(got), 'the exported file differs from design/bom.csv (filtered or re-quoted?)').toBe(sha256(want))
  const records = parseCsv(got.toString('utf8'))
  expect(records.length - 1, 'a CSV reader finds a different number of records than the parts total').toBe(totals.lines)
  expect(w.errors, `console or http errors: ${w.errors.join(' | ')}`).toEqual([])
})

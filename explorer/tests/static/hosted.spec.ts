// Hosted-ready check: the built folder must work from a plain static host under a sub-path.
// Builds the app (npm run build equivalent: vite build + stage-static), serves dist/ with a plain static
// server under /ring/, loads the home route and asserts: 0 console errors, the manifest answers 200, one
// listed design file answers 200 from files/, and nothing absolute (localhost, a port, a home path)
// is written in the build. HOSTED_ENTRY=<html> builds that entry instead of index.html (to prove the
// mechanics before the shell exists); EXPLORER_BUNDLE / EXPLORER_SOURCE pick the data.
import { expect, test } from '@playwright/test'
import { execFileSync } from 'node:child_process'
import { cpSync } from 'node:fs'
import { existsSync, mkdtempSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, relative } from 'node:path'
import { EXPLORER_ROOT, FIXTURE_DATA, FIXTURE_SOURCE, SAMPLE_BUNDLE, serveStatic, watchConsole, type StaticSite } from '../support'

const page0 = process.env.HOSTED_ENTRY ? relative(EXPLORER_ROOT, process.env.HOSTED_ENTRY) : ''
const bundle = process.env.EXPLORER_BUNDLE ?? (existsSync(FIXTURE_DATA) ? FIXTURE_DATA : SAMPLE_BUNDLE)
const source = process.env.EXPLORER_SOURCE ?? (existsSync(FIXTURE_DATA) ? FIXTURE_SOURCE : join(EXPLORER_ROOT, 'tests', 'support', 'sample-source'))

function* walk(dir: string): Generator<string> {
  for (const n of readdirSync(dir)) {
    const p = join(dir, n)
    if (statSync(p).isDirectory()) yield* walk(p)
    else yield p
  }
}

let site: StaticSite
let dist: string

test.beforeAll(async () => {
  dist = mkdtempSync(join(tmpdir(), 'explorer-dist-'))
  const env = { ...process.env, EXPLORER_BUNDLE: bundle, EXPLORER_SOURCE: source }
  execFileSync('npx', ['vite', 'build', '--outDir', dist, '--emptyOutDir'], { cwd: EXPLORER_ROOT, env, stdio: 'pipe' })
  execFileSync('node', ['scripts/stage-static.mjs', '--out', dist], { cwd: EXPLORER_ROOT, env, stdio: 'pipe' })
  site = await serveStatic(dist, '/ring/')
})
test.afterAll(async () => {
  await site?.stop()
})

test('hosted: the built folder works from a plain static host under /ring/', async ({ page, request }) => {
  const w = watchConsole(page)
  const seen: string[] = []
  page.on('response', (r) => seen.push(r.url()))
  await page.goto(site.url + page0)
  await page.waitForLoadState('load')
  await page.waitForTimeout(1500)
  expect(w.errors, w.errors.join('\n')).toEqual([])
  // the app itself read its data by a relative url that resolved under /ring/
  expect(seen.some((u) => u === site.url + 'data/manifest.json'), seen.join('\n')).toBe(true)
  expect((await request.get(site.url + 'data/manifest.json')).status()).toBe(200)
  const files = JSON.parse(readFileSync(join(dist, 'data', 'files.json'), 'utf8')) as { files: { path: string }[] }
  const first = files.files[0]
  expect(first, 'files.json lists at least one file').toBeTruthy()
  const r = await request.get(site.url + 'files/' + first!.path.split('/').map(encodeURIComponent).join('/'))
  expect(r.status()).toBe(200)
  // a file that is not listed is not in the build
  expect((await request.get(site.url + 'files/design/.venv/bin/python')).status()).toBe(404)
  if (!process.env.EXPLORER_SOURCE && !existsSync(FIXTURE_DATA)) {
    expect((await request.get(site.url + 'files/sample/unlisted.txt')).status(), 'an unlisted file is not copied').toBe(404)
  }
})

test('hosted: no absolute address or path is written in the build or the bundle', async () => {
  const bad = /(https?:\/\/(localhost|127\.0\.0\.1)|localhost:\d+|127\.0\.0\.1:\d+|file:\/\/|["'`]\/(Users|home|private|tmp|var)\/)/
  const hits: string[] = []
  for (const f of walk(dist)) {
    if (!/\.(js|mjs|css|html|json|map)$/.test(f)) continue
    const m = bad.exec(readFileSync(f, 'utf8'))
    if (m) hits.push(`${f.slice(dist.length)}: ${m[0]}`)
  }
  expect(hits, hits.join('\n')).toEqual([])
})

test('hosted: the part notes travel with the collector bundle and answer 200 under /ring/', async ({ request }) => {
  // collector -> bundle (with content/part-notes.json) -> staged copy of the build -> plain static server
  const tmp = mkdtempSync(join(tmpdir(), 'explorer-notes-'))
  const py = process.env.COLLECT_PY ?? join(EXPLORER_ROOT, '..', 'design', '.venv', 'bin', 'python')
  execFileSync(py, ['collector/run.py', '--source', source, '--commit', '0'.repeat(40), '--out', join(tmp, 'bundle'), '--extractors', join(tmp, 'none'), '--content', join(SAMPLE_BUNDLE, 'content')], { cwd: EXPLORER_ROOT, stdio: 'pipe' })
  const dist2 = join(tmp, 'dist')
  cpSync(dist, dist2, { recursive: true })
  execFileSync('node', ['scripts/stage-static.mjs', '--out', dist2, '--bundle', join(tmp, 'bundle'), '--source', source], { cwd: EXPLORER_ROOT, stdio: 'pipe' })
  const site2 = await serveStatic(dist2, '/ring/')
  try {
    const r = await request.get(site2.url + 'data/content/part-notes.json')
    expect(r.status(), 'part notes must be in the built bundle').toBe(200)
    expect(Object.keys((await r.json()).notes).length).toBeGreaterThan(0)
  } finally {
    await site2.stop()
  }
})

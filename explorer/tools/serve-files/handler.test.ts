// @vitest-environment node
import { mkdirSync, mkdtempSync, symlinkSync, writeFileSync } from 'node:fs'
import { createServer, type Server } from 'node:http'
import type { AddressInfo } from 'node:net'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import { createHandler, safeRelative } from './handler'

let server: Server
let base: string
let emptyServer: Server
let emptyBase: string

const listen = async (h: ReturnType<typeof createHandler>) => {
  const s = createServer((req, res) => h(req, res, () => { res.statusCode = 200; res.end('next') }))
  await new Promise<void>((r) => s.listen(0, '127.0.0.1', r))
  return { s, url: `http://127.0.0.1:${(s.address() as AddressInfo).port}` }
}

beforeAll(async () => {
  const tmp = mkdtempSync(join(tmpdir(), 'serve-files-'))
  const repo = join(tmp, 'repo')
  const bundle = join(tmp, 'bundle')
  mkdirSync(join(repo, 'design', 'datasheets'), { recursive: true })
  mkdirSync(join(repo, 'design', '.venv', 'bin'), { recursive: true })
  mkdirSync(bundle)
  writeFileSync(join(repo, 'design', 'datasheets', 'zz.pdf'), '%PDF-zz')
  writeFileSync(join(repo, 'design', 'secret.txt'), 'not listed')
  writeFileSync(join(repo, 'design', '.venv', 'bin', 'python'), 'x')
  writeFileSync(join(tmp, 'outside.txt'), 'outside the repo')
  symlinkSync(join(tmp, 'outside.txt'), join(repo, 'design', 'link.txt'))
  writeFileSync(join(bundle, 'files.json'), JSON.stringify({ files: [{ path: 'design/datasheets/zz.pdf' }, { path: 'design/link.txt' }] }))
  writeFileSync(join(bundle, 'manifest.json'), '{"ok":true}')
  ;({ s: server, url: base } = await listen(createHandler({ repoRoot: repo, bundleDir: bundle })))
  ;({ s: emptyServer, url: emptyBase } = await listen(createHandler({ repoRoot: repo, bundleDir: join(tmp, 'no-such-bundle') })))
})
afterAll(async () => {
  await new Promise<void>((r) => server.close(() => r()))
  await new Promise<void>((r) => emptyServer.close(() => r()))
})

const get = (p: string, init?: RequestInit) => fetch(base + p, init)

describe('/files', () => {
  it('serves a listed file with its type', async () => {
    const r = await get('/files/design/datasheets/zz.pdf')
    expect(r.status).toBe(200)
    expect(r.headers.get('content-type')).toBe('application/pdf')
    expect(await r.text()).toBe('%PDF-zz')
  })
  it('supports HEAD and download', async () => {
    expect((await get('/files/design/datasheets/zz.pdf', { method: 'HEAD' })).status).toBe(200)
    expect((await get('/files/design/datasheets/zz.pdf?download=1')).headers.get('content-disposition')).toBe('attachment')
  })
  it('refuses a file that is not listed in files.json', async () => {
    expect((await get('/files/design/secret.txt')).status).toBe(404)
    expect((await get('/files/design/.venv/bin/python')).status).toBe(404)
  })
  it('refuses traversal, encoded or not', async () => {
    expect((await get('/files/..%2F..%2Fetc%2Fpasswd')).status).toBe(404)
    expect((await get('/files/design/%2e%2e/design/secret.txt')).status).toBe(404)
    expect((await get('/files/design%2F..%2Fdesign%2Fsecret.txt')).status).toBe(404)
  })
  it('refuses a listed path whose real file lies outside the repo', async () => {
    expect((await get('/files/design/link.txt')).status).toBe(404)
  })
  it('refuses writes', async () => {
    expect((await get('/files/design/datasheets/zz.pdf', { method: 'POST' })).status).toBe(405)
    expect((await get('/data/manifest.json', { method: 'PUT' })).status).toBe(405)
  })
})

describe('/data', () => {
  it('serves the bundle files', async () => {
    const r = await get('/data/manifest.json')
    expect(r.status).toBe(200)
    expect(await r.json()).toEqual({ ok: true })
  })
  it('does not leave the bundle', async () => {
    expect((await get('/data/..%2Frepo%2Fdesign%2Fsecret.txt')).status).toBe(404)
  })
  it('answers 404 for every path when the bundle folder is empty or absent', async () => {
    expect((await fetch(emptyBase + '/data/manifest.json')).status).toBe(404)
    expect((await fetch(emptyBase + '/files/design/datasheets/zz.pdf')).status).toBe(404)
  })
  it('passes other paths on', async () => {
    expect(await (await get('/inside')).text()).toBe('next')
  })
})

describe('safeRelative', () => {
  it('refuses traversal, absolute, backslash, NUL and bad escapes', () => {
    for (const bad of ['..%2F..%2Fetc%2Fpasswd', '../x', 'a/../b', '%2Fetc', 'a%5Cb', 'a%00b', '', 'a//b', '%E0%A4%A']) expect(safeRelative(bad)).toBeNull()
    expect(safeRelative('design/datasheets/a%20b.pdf')).toBe('design/datasheets/a b.pdf')
  })
})

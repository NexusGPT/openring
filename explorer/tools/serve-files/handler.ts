// Read-only file serving for the explorer. Two routes:
//   /data/<path>   the active data bundle (EXPLORER_BUNDLE, default public/data)
//   /files/<path>  a design file from the repo root, ONLY when <path> is listed in the bundle's files.json
// Nothing else is served from here, nothing is ever written, and a path that leaves its root is a 404.
import { createReadStream, existsSync, readFileSync, realpathSync, statSync } from 'node:fs'
import type { IncomingMessage, ServerResponse } from 'node:http'
import { extname, join, resolve, sep } from 'node:path'

export interface ServeFilesOptions {
  /** root of the repository the design lives in (parent of the explorer folder by default) */
  repoRoot: string
  /** folder holding manifest.json, files.json and the other records */
  bundleDir: string
}

const TYPES: Record<string, string> = {
  '.json': 'application/json; charset=utf-8',
  '.pdf': 'application/pdf',
  '.md': 'text/markdown; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.csv': 'text/csv; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.zip': 'application/zip',
}

/** Decode a URL path tail and refuse anything that could leave its root. Returns null when unsafe. */
export function safeRelative(tail: string): string | null {
  let decoded: string
  try {
    decoded = decodeURIComponent(tail)
  } catch {
    return null
  }
  if (!decoded || decoded.includes('\0') || decoded.includes('\\') || decoded.startsWith('/')) return null
  const parts = decoded.split('/')
  if (parts.some((p) => p === '..' || p === '.' || p === '')) return null
  return parts.join('/')
}

function inside(root: string, candidate: string): boolean {
  const r = realpathSync(root)
  return candidate === r || candidate.startsWith(r + sep)
}

function listedPaths(bundleDir: string): Set<string> {
  const f = join(bundleDir, 'files.json')
  if (!existsSync(f)) return new Set()
  try {
    const j = JSON.parse(readFileSync(f, 'utf8')) as { files?: { path: string }[] }
    return new Set((j.files ?? []).map((x) => x.path))
  } catch {
    return new Set()
  }
}

function notFound(res: ServerResponse): void {
  res.statusCode = 404
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.setHeader('Cache-Control', 'no-store')
  res.end('{"error":"not found"}')
}

function send(res: ServerResponse, method: string, abs: string, download: boolean): void {
  const type = TYPES[extname(abs).toLowerCase()] ?? 'application/octet-stream'
  res.statusCode = 200
  res.setHeader('Content-Type', type)
  res.setHeader('Content-Length', String(statSync(abs).size))
  res.setHeader('Cache-Control', 'no-store')
  res.setHeader('X-Content-Type-Options', 'nosniff')
  if (type.startsWith('image/svg')) res.setHeader('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'")
  res.setHeader('Content-Disposition', download ? 'attachment' : 'inline')
  if (method === 'HEAD') return void res.end()
  createReadStream(abs).pipe(res)
}

export function createHandler(opts: ServeFilesOptions) {
  const repoRoot = resolve(opts.repoRoot)
  const bundleDir = resolve(opts.bundleDir)
  return (req: IncomingMessage, res: ServerResponse, next: () => void): void => {
    const url = req.url ?? ''
    const q = url.indexOf('?')
    const path = q < 0 ? url : url.slice(0, q)
    const download = q >= 0 && new URLSearchParams(url.slice(q + 1)).get('download') === '1'
    const isData = path.startsWith('/data/')
    const isFile = path.startsWith('/files/')
    if (!isData && !isFile) return next()
    const method = req.method ?? 'GET'
    if (method !== 'GET' && method !== 'HEAD') {
      res.statusCode = 405
      res.setHeader('Allow', 'GET, HEAD')
      return void res.end()
    }
    const rel = safeRelative(path.slice(isData ? '/data/'.length : '/files/'.length))
    if (rel === null) return notFound(res)
    try {
      if (isFile && !listedPaths(bundleDir).has(rel)) return notFound(res)
      const root = isData ? bundleDir : repoRoot
      if (!existsSync(root)) return notFound(res)
      const abs = join(root, rel)
      if (!existsSync(abs)) return notFound(res)
      const real = realpathSync(abs)
      if (!inside(root, real) || !statSync(real).isFile()) return notFound(res)
      send(res, method, real, download)
    } catch {
      notFound(res)
    }
  }
}

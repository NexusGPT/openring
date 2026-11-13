// A plain static file server (node http, no vite) for the hosted-build check. It serves a folder under
// a sub-path, on a free port, 127.0.0.1 only. Anything outside the sub-path is 404, like a host that
// puts the app in a folder. Paths that are not files under the sub-path fall back to index.html.
import { createReadStream, existsSync, statSync } from 'node:fs'
import { createServer, type Server } from 'node:http'
import type { AddressInfo } from 'node:net'
import { extname, join, normalize, sep } from 'node:path'

const TYPES: Record<string, string> = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.pdf': 'application/pdf',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.glb': 'model/gltf-binary', '.zip': 'application/zip',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.csv': 'text/csv', '.md': 'text/markdown', '.txt': 'text/plain',
}

export interface StaticSite {
  /** e.g. http://127.0.0.1:53211/ring/ */
  url: string
  port: number
  stop(): Promise<void>
}

export async function serveStatic(dir: string, subPath = '/ring/'): Promise<StaticSite> {
  const base = subPath.endsWith('/') ? subPath : subPath + '/'
  const server: Server = createServer((req, res) => {
    const u = new URL(req.url ?? '/', 'http://x')
    if (!u.pathname.startsWith(base)) {
      res.statusCode = 404
      return void res.end('not found')
    }
    let rel: string
    try {
      rel = decodeURIComponent(u.pathname.slice(base.length))
    } catch {
      res.statusCode = 400
      return void res.end()
    }
    const abs = normalize(join(dir, rel))
    let file = abs.startsWith(dir + sep) || abs === dir ? abs : ''
    if (file && existsSync(file) && statSync(file).isDirectory()) file = join(file, 'index.html')
    const isAsset = /\.[a-z0-9]+$/i.test(rel) || rel.startsWith('data/') || rel.startsWith('files/') || !existsSync(join(dir, 'index.html'))
    if (!file || !existsSync(file)) {
      if (isAsset) {
        res.statusCode = 404
        return void res.end('not found')
      }
      file = join(dir, 'index.html')
    }
    res.setHeader('Content-Type', TYPES[extname(file).toLowerCase()] ?? 'application/octet-stream')
    createReadStream(file).pipe(res)
  })
  await new Promise<void>((r) => server.listen(0, '127.0.0.1', r))
  const port = (server.address() as AddressInfo).port
  return { url: `http://127.0.0.1:${port}${base}`, port, stop: () => new Promise((r) => server.close(() => r())) }
}

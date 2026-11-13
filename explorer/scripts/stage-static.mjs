#!/usr/bin/env node
// Makes dist/ a complete static site: copies the data bundle to dist/data/ and every file listed in
// files.json (allow-list only) to dist/files/<path>. After this, nothing at run time needs the dev
// server. The partner bundle zip is built by the collector and is already inside the data bundle.
//   node scripts/stage-static.mjs [--out dist] [--bundle <dir>] [--source <repo root>]
//   defaults: EXPLORER_BUNDLE or public/data; EXPLORER_SOURCE or the parent folder.
import { cpSync, existsSync, mkdirSync, readFileSync, realpathSync, rmSync, statSync } from 'node:fs'
import { dirname, join, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const arg = (n) => {
  const i = process.argv.indexOf(n)
  return i > 0 ? process.argv[i + 1] : undefined
}
const out = resolve(root, arg('--out') ?? 'dist')
const bundle = resolve(arg('--bundle') ?? process.env.EXPLORER_BUNDLE ?? join(root, 'public', 'data'))
const source = resolve(arg('--source') ?? process.env.EXPLORER_SOURCE ?? join(root, '..'))

if (!existsSync(out)) {
  console.error(`stage-static: ${out} does not exist; run vite build first`)
  process.exit(1)
}
rmSync(join(out, 'data'), { recursive: true, force: true })
rmSync(join(out, 'files'), { recursive: true, force: true })

if (!existsSync(bundle)) {
  console.log(`stage-static: no data bundle at ${bundle}; the site will say "Not built yet" on every screen`)
  process.exit(0)
}
cpSync(bundle, join(out, 'data'), { recursive: true })

const listFile = join(bundle, 'files.json')
let copied = 0
const problems = []
if (existsSync(listFile)) {
  const listed = JSON.parse(readFileSync(listFile, 'utf8')).files ?? []
  const realSource = realpathSync(source)
  for (const { path } of listed) {
    const parts = path.split('/')
    if (path.startsWith('/') || path.includes('\0') || path.includes('\\') || parts.some((p) => p === '..' || p === '.' || p === '')) {
      problems.push(`unsafe path ${path}`)
      continue
    }
    const from = join(source, path)
    if (!existsSync(from)) {
      problems.push(`listed but not on disk: ${path}`)
      continue
    }
    const real = realpathSync(from)
    if (!real.startsWith(realSource + sep) || !statSync(real).isFile()) {
      problems.push(`not a file inside the repo: ${path}`)
      continue
    }
    const to = join(out, 'files', path)
    mkdirSync(dirname(to), { recursive: true })
    cpSync(real, to)
    copied++
  }
}
console.log(`stage-static: data bundle copied; ${copied} design file(s) copied to files/`)
if (problems.length) {
  console.error('stage-static: files.json lists files the build cannot copy:\n  ' + problems.slice(0, 10).join('\n  '))
  process.exit(1)
}

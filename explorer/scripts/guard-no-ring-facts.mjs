#!/usr/bin/env node
// Guard: no ring fact is written in app source. Reads the data bundle(s), collects distinctive tokens
// (part refs, maker part numbers, firmware state ids and labels, finish names, look titles, size
// strings) and searches src/** (test files excluded). Exit 1 names each file and token found.
//   bundles: tests/support/sample-bundle (always), .cache/fixture-99dfb85/data (when built),
//            plus any folder in GUARD_BUNDLE (colon-separated).
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const bundles = [join(root, 'tests', 'support', 'sample-bundle'), join(root, '.cache', 'fixture-99dfb85', 'data')]
if (process.env.GUARD_BUNDLE) bundles.push(...process.env.GUARD_BUNDLE.split(':').filter(Boolean))

const readJson = (dir, rel) => {
  const f = join(dir, rel)
  if (!existsSync(f)) return null
  try {
    return JSON.parse(readFileSync(f, 'utf8'))
  } catch {
    return null
  }
}

function tokensOf(dir) {
  const t = new Set()
  const add = (v) => typeof v === 'string' && v.trim().length >= 2 && t.add(v.trim())
  const parts = readJson(dir, 'parts.json')
  for (const l of parts?.lines ?? []) {
    ;(l.refs ?? []).forEach(add)
    add(l.maker_part_number)
  }
  const beh = readJson(dir, 'behaviour.json')
  for (const s of beh?.states ?? []) (add(s.id), add(s.label))
  const looks = readJson(dir, 'looks/index.json')
  for (const f of looks?.finishes ?? []) add(f.name)
  for (const o of looks?.options ?? []) add(o.title)
  const facts = readJson(dir, 'facts.json')
  for (const f of facts?.facts ?? []) if (typeof f.value === 'string' && /\d\s*x\s*\d/.test(f.value)) add(f.value)
  const caseIdx = readJson(dir, 'case/index.json')
  for (const f of caseIdx?.facts ?? []) if (typeof f.value === 'string' && /\d\s*x\s*\d/.test(f.value)) add(f.value)
  return t
}

const present = bundles.filter((b) => existsSync(b))
const tokens = new Set()
for (const b of present) for (const x of tokensOf(b)) tokens.add(x)

function* walk(dir) {
  for (const n of readdirSync(dir)) {
    const p = join(dir, n)
    if (statSync(p).isDirectory()) yield* walk(p)
    else yield p
  }
}
const isTest = (p) => /\.(test|spec)\.[tj]sx?$/.test(p) || p.includes('__checks__') || p.includes('__tests__')
const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const hits = []
const srcDir = join(root, 'src')
for (const file of existsSync(srcDir) ? walk(srcDir) : []) {
  if (isTest(file) || !/\.(tsx?|jsx?|css|html|json)$/.test(file) || file.endsWith('records.ts')) continue
  const text = readFileSync(file, 'utf8')
  for (const tok of tokens) {
    const re = new RegExp(`(?<![A-Za-z0-9_])${escape(tok)}(?![A-Za-z0-9_])`)
    if (re.test(text)) hits.push(`${relative(root, file)}: '${tok}'`)
  }
}

// No file loads from the internet: no external http(s) address in app source or index.html.
const ALLOWED_HOST = /^https?:\/\/www\.w3\.org([:/]|$)/
const LOCAL = /(?<![\w.])(localhost|127\.0\.0\.1)(?![\w.])/
const netFiles = [...(existsSync(srcDir) ? walk(srcDir) : []), join(root, 'index.html')].filter(
  (f) => existsSync(f) && !isTest(f) && /\.(tsx?|jsx?|css|html)$/.test(f) && !f.endsWith('records.ts'),
)
for (const file of netFiles) {
  const text = readFileSync(file, 'utf8')
  const lm = LOCAL.exec(text)
  if (lm) hits.push(`${relative(root, file)}: local address '${lm[0]}' (use relative urls)`)
  for (const m of text.matchAll(/https?:\/\/[^\s'"`)>]+/g)) {
    if (!ALLOWED_HOST.test(m[0])) hits.push(`${relative(root, file)}: external address '${m[0]}'`)
  }
}

console.log(`guard-no-ring-facts: ${tokens.size} tokens from ${present.length} bundle(s)` + (present.length < bundles.length ? ' (fixture bundle not built: sample bundle only)' : ''))
if (hits.length) {
  console.error('ring facts found in app source (every value must come from the data bundle):')
  for (const h of hits) console.error('  ' + h)
  process.exit(1)
}
console.log('guard-no-ring-facts: clean')

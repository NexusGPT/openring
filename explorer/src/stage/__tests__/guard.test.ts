// The stage names no part, no state, no finish and no address: every such value comes from the bundle.
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { EXTERIOR_NODES, INTERNAL_NODES, RING } from './harness-data'

const dir = join(__dirname, '..')
const sources = readdirSync(dir).filter((f) => /\.(ts|tsx|html)$/.test(f) && !f.startsWith('harness'))
// 'band' is also a field of the ring-model record (ring.band), read by name; the other words are node kinds
const KINDS = new Set(['band', 'finish metal', 'glass', 'screen', 'light', 'satin', 'matte', 'gold', 'plain'])
const text = (f: string) => readFileSync(join(dir, f), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|\s)\/\/.*$/gm, '$1')

describe('stage source guard', () => {
  it('has no node name, layer id or screen state from the records', () => {
    const tokens = new Set<string>([...EXTERIOR_NODES, ...INTERNAL_NODES].flatMap((n) => [n.name, n.layer ?? '']).concat(RING.screens.states.flatMap((s) => [s.state, s.label, ...s.fields.map((f) => f.label ?? '')])).filter((t) => t.length >= 3 && !KINDS.has(t)))
    const hits: string[] = []
    for (const f of sources) for (const t of tokens) if (new RegExp(`(?<![A-Za-z0-9_])${t}(?![A-Za-z0-9_])`).test(text(f))) hits.push(`${f}: ${t}`)
    expect(hits).toEqual([])
  })
  it('loads nothing from the internet: no http(s) address and no cdn', () => {
    const hits = sources.filter((f) => /https?:\/\/|cdn\./i.test(text(f)))
    expect(hits).toEqual([])
  })
})

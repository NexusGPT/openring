import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const dir = join(__dirname, '..')
const HEX = /#[0-9a-fA-F]{3,8}\b|\brgba?\(/

/** Colours live in src/styles/tokens.css only. The one literal waiting on a token request carries 'REQUEST' on its line. */
export function hexLines(css: string): string[] {
  return css.split('\n').filter((l) => HEX.test(l) && !l.includes('REQUEST'))
}

describe('part card colours', () => {
  it('part-card-C11: no hex or rgb colour in PartCard css except the one marked REQUEST', () => {
    for (const f of readdirSync(dir).filter((n) => n.endsWith('.css'))) {
      expect(hexLines(readFileSync(join(dir, f), 'utf8')), f).toEqual([])
    }
  })
  it('part-card-C12: the check itself catches a hex colour and an rgb() colour', () => {
    expect(hexLines('.a { color: #fff; }')).toHaveLength(1)
    expect(hexLines('.a { color: rgb(0 0 0); }')).toHaveLength(1)
    expect(hexLines('.a { color: var(--ink); }')).toHaveLength(0)
  })
})

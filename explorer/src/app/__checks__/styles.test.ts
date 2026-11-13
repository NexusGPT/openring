// shell-C05: the look rules of S1 Gallery, read from the stylesheets.
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { expect, test } from 'vitest'

const SRC = join(__dirname, '..', '..')
const files = (dir: string): string[] =>
  readdirSync(dir).flatMap((n) => {
    const p = join(dir, n)
    return statSync(p).isDirectory() ? (n === 'node_modules' ? [] : files(p)) : p.endsWith('.css') ? [p] : []
  })
// The shell owns src/styles, src/app and main.tsx; other pieces keep their own stylesheets (see the
// seams check for the whole tree).
const css = files(SRC).filter((p) => /^(styles|app)[\\/]/.test(relative(SRC, p))).map((p) => ({ name: relative(SRC, p), text: readFileSync(p, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '') }))
const HEX = /#[0-9a-fA-F]{3,8}\b/

test('shell-C05a: hex colours appear only in styles/tokens.css', () => {
  const bad = css.filter((f) => f.name !== join('styles', 'tokens.css') && HEX.test(f.text)).map((f) => f.name)
  expect(bad).toEqual([])
  expect(css.find((f) => f.name === join('styles', 'tokens.css'))?.text).toMatch(HEX)
})

test('shell-C05b: the brand and display text use Libre Caslon Text, body text Geist, labels Geist Mono', () => {
  const tokens = css.find((f) => f.name === join('styles', 'tokens.css'))?.text ?? ''
  expect(tokens).toMatch(/--font-display:\s*'Libre Caslon Text'/)
  expect(tokens).toMatch(/--font-text:\s*'Geist Sans'/)
  expect(tokens).toMatch(/--font-label:\s*'Geist Mono'/)
  const shell = css.find((f) => f.name === join('styles', 'shell.css'))?.text ?? ''
  expect(shell).toMatch(/\.brand\s*\{[^}]*font-family:\s*var\(--font-display\)/)
})

test('shell-C05c: no shadow anywhere, no rounded corner except the 999px pill', () => {
  const shadows: string[] = []
  const radii: string[] = []
  for (const f of css) {
    for (const m of f.text.matchAll(/box-shadow\s*:\s*([^;}]+)/g)) if (m[1]?.trim() !== 'none') shadows.push(`${f.name}: ${m[0]}`)
    for (const m of f.text.matchAll(/border-radius\s*:\s*([^;}]+)/g)) {
      const v = m[1]?.trim() ?? ''
      if (!/^(0|0px|var\(--radius-pill\)|999px)$/.test(v)) radii.push(`${f.name}: ${m[0]}`)
    }
  }
  expect(shadows).toEqual([])
  expect(radii).toEqual([])
})

test('shell-C05d: the tab bar is 56 px and the stage takes 1.55 parts to the panel 1', () => {
  const tokens = css.find((f) => f.name === join('styles', 'tokens.css'))?.text ?? ''
  expect(tokens).toMatch(/--bar-h:\s*56px/)
  expect(tokens).toMatch(/--stage-fr:\s*1\.55fr/)
  expect(tokens).toMatch(/--panel-fr:\s*1fr/)
})

test('shell-C05e: the plain body text colour is the --text token, written once in tokens.css', () => {
  const tokens = css.find((f) => f.name === join('styles', 'tokens.css'))?.text ?? ''
  expect(tokens).toMatch(/--text:\s*#33373d;/)
  const elsewhere = css.filter((f) => f.name !== join('styles', 'tokens.css') && /#33373d/i.test(f.text)).map((f) => f.name)
  expect(elsewhere).toEqual([])
})

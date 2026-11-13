// Where the data bundles live. A journey or check reads one of three:
//   fixture  .cache/fixture-99dfb85/data (the frozen A3 copy, made by tests/fixtures/make-fixture.sh)
//   sample   tests/support/sample-bundle (made-up values, in git; for the contract's own tests)
//   empty    a fresh empty folder (every record reads 'missing')
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

export const EXPLORER_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..')
export const FIXTURE_DATA = join(EXPLORER_ROOT, '.cache', 'fixture-99dfb85', 'data')
export const FIXTURE_SOURCE = join(EXPLORER_ROOT, '.cache', 'fixture-99dfb85', 'src')
export const SAMPLE_BUNDLE = join(EXPLORER_ROOT, 'tests', 'support', 'sample-bundle')

export function emptyBundle(): string {
  return mkdtempSync(join(tmpdir(), 'explorer-empty-bundle-'))
}

/** The environment a server needs to show one bundle. */
export function bundleEnv(bundle: string, source?: string): Record<string, string> {
  return { EXPLORER_BUNDLE: bundle, ...(source ? { EXPLORER_SOURCE: source } : {}) }
}

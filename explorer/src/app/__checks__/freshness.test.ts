// shell-C04 (unit side): the stamp is built from the manifest, never from a fixed string or the clock.
import { afterEach, expect, test, vi } from 'vitest'
import { stampOf } from '../freshness'

const base = { built_at: '2026-11-10T14:05:09+00:00', git_commit: 'abcdef0123456789', git_dirty: false }

afterEach(() => vi.useRealTimers())

test('shell-C04a: the stamp is built_at in the browser locale plus the first 7 characters of the commit', () => {
  const s = stampOf(base, 'en-GB')
  expect(s.text).toBe(`Data built ${new Date(base.built_at).toLocaleString('en-GB')} · commit abcdef0`)
  expect(s.dirty).toBe(false)
  expect(s.text).not.toContain('files changed since')
})

test('shell-C04b: a dirty design adds "files changed since"', () => {
  const s = stampOf({ ...base, git_dirty: true }, 'en-GB')
  expect(s.text.endsWith(' · files changed since')).toBe(true)
  expect(s.dirty).toBe(true)
})

test('shell-C04c: the stamp does not follow the clock', () => {
  vi.useFakeTimers()
  vi.setSystemTime(new Date('2031-01-01T00:00:00Z'))
  expect(stampOf(base, 'en-GB').text).toContain(new Date(base.built_at).toLocaleString('en-GB'))
  expect(stampOf(base, 'en-GB').text).not.toContain('2031')
})

test('shell-C04d: two builds give two stamps', () => {
  expect(stampOf({ ...base, git_commit: '1111111zzz' }).text).not.toBe(stampOf(base).text)
})

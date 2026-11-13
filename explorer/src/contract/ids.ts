// Grammars shared by every screen and every test.
import type { Bom, PartId } from './records'

/** The 9 routes of the app, in tab order. */
export const ROUTES = ['home', 'look', 'inside', 'electronics', 'board', 'parts', 'behaviour', 'case', 'open'] as const
export type RouteId = (typeof ROUTES)[number]
/** `app` is the shell itself (tab bar, panel frame, freshness stamp). */
export type TestScope = RouteId | 'app'

/** data-testid grammar: '<route>.<element>', element in kebab-case. A shared component takes the
 *  route that hosts it (inside.part-card, parts.part-card); the shell uses 'app'. */
export type TestId = `${TestScope}.${string}`
export const TESTID_RE = /^(app|home|look|inside|electronics|board|parts|behaviour|case|open)\.[a-z][a-z0-9]*(-[a-z0-9]+)*$/
export function testId(scope: TestScope, element: string): TestId {
  const id = `${scope}.${element}`
  if (!TESTID_RE.test(id)) throw new Error(`bad test id '${id}': use <route>.<element> with a kebab-case element`)
  return id as TestId
}

/** Part id grammar: '<bom>:<ref>' with bom in {ring, case}; the ref is the token from the bom reference cell. */
export const PART_ID_RE = /^(ring|case):[A-Za-z0-9][A-Za-z0-9_.+/-]*$/
export function partId(bom: Bom, ref: string): PartId {
  const id = `${bom}:${ref}`
  if (!PART_ID_RE.test(id)) throw new Error(`bad part id '${id}'`)
  return id
}
export function parsePartId(id: string): { bom: Bom; ref: string } | null {
  if (!PART_ID_RE.test(id)) return null
  const i = id.indexOf(':')
  return { bom: id.slice(0, i) as Bom, ref: id.slice(i + 1) }
}

/** Check id grammar for the checks of one lane: '<lane>-C01..C99'. */
export const CHECK_ID_RE = /^[a-z][a-z0-9-]*-C(0[1-9]|[1-9][0-9])$/

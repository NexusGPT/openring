// The words of every honest state. Banners and pills take their text from here and nowhere else;
// the seam check greps the app for sentences that duplicate these. No ring fact is written here.
import type { AreaState } from './records'

/** Area pill words, exactly as the owner reads them. A total record: a new state is a build error. */
export const AREA_PILL: Record<AreaState, string> = {
  done: 'done',
  'in progress': 'in progress',
  'not started': 'not started',
  'waiting on a supplier': 'waiting on a supplier',
  'state unknown': 'state unknown',
}
export const AREA_PILL_WORDS: readonly string[] = Object.values(AREA_PILL)

/** One plain sentence and one next action per honest state. */
export interface Banner {
  sentence: string
  action: string
}

export type BannerSpec =
  | { kind: 'missing' }
  | { kind: 'unparsed'; file: string }
  | { kind: 'stale'; basis: string; current: string }
  | { kind: 'exterior-not-picked' }
  | { kind: 'exterior-in-design' }
  | { kind: 'new-options' }
  | { kind: 'board-not-routed'; missing: readonly string[] }

type Kind = BannerSpec['kind']
type Of<K extends Kind> = Extract<BannerSpec, { kind: K }>

const BUILDERS: { [K in Kind]: (spec: Of<K>) => Banner } = {
  missing: () => ({ sentence: 'Not built yet.', action: 'Run npm run collect.' }),
  unparsed: (s) => ({
    sentence: `The file changed and cannot be read: ${s.file}.`,
    action: 'Fix the file, then run npm run collect.',
  }),
  stale: (s) => ({
    sentence: `Made for design ${s.basis}; the design is now ${s.current}.`,
    action: 'Being redone.',
  }),
  'exterior-not-picked': () => ({
    sentence: 'Exterior not designed yet.',
    action: "The stage shows a plain black slab at the ring's true size.",
  }),
  'exterior-in-design': () => ({
    sentence: 'Exterior in design, not approved yet.',
    action: 'The stage shows the model drawn so far.',
  }),
  'new-options': () => ({
    sentence: 'New options in design.',
    action: 'They appear here when they are ready to compare.',
  }),
  'board-not-routed': (s) => ({
    sentence: `Board not routed yet.${s.missing.length ? ` Missing: ${s.missing.join(', ')}.` : ''}`,
    action: 'The plan shows where the parts sit.',
  }),
}

export function banner(spec: BannerSpec): Banner {
  return (BUILDERS[spec.kind] as (s: BannerSpec) => Banner)(spec)
}

/** The full banner text: sentence, a space, action. */
export function bannerText(spec: BannerSpec): string {
  const b = banner(spec)
  return `${b.sentence} ${b.action}`
}

/** Short strings shared by several screens. */
export const WORDS = {
  noPartsLine: 'no parts-list line for this object',
  notOnDisk: 'not on disk',
  nothingWaiting: 'nothing waiting',
  stateUnknown: AREA_PILL['state unknown'],
  runCollect: 'npm run collect',
} as const

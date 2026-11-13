// What the Look screen shows, decided from the two records it reads. Pure: no ring fact is written here.
import type { LookOptions, RingModel } from '../../contract'

export type LookOption = LookOptions['options'][number]

export const LOOK_WORDS = {
  title: 'Look',
  options: 'Options',
  finish: 'Finish',
  screen: 'Screen',
  view: 'View',
  off: 'Off',
  picked: 'Picked',
  details: 'Details',
  worseAt: 'Worse at',
  noFinishes: 'No finishes in the bundle yet.',
  fallback: 'Exterior',
  source: 'Source',
  more: 'More',
  fewer: 'Fewer',
} as const

/** The view presets the stage knows, with the owner's words. */
export const VIEW_CHOICES = [
  { id: 'three-quarter', label: 'Three-quarter' },
  { id: 'top', label: 'Top' },
  { id: 'side', label: 'Side' },
  { id: 'finger', label: 'On a finger' },
] as const
export type ViewId = (typeof VIEW_CHOICES)[number]['id']

/** The options the owner may see now: never a rejected one; once one is picked, that one alone. */
export function shownOptions(looks: LookOptions | null): LookOption[] {
  if (!looks) return []
  const open = looks.options.filter((o) => !o.rejected)
  return looks.picked ? open.filter((o) => o.id === looks.picked) : open
}

export type Mode =
  | { kind: 'options'; options: LookOption[] } // the look-options record lists open options
  | { kind: 'none' } // the record is readable and holds no open option: "New options in design"
  | { kind: 'fallback' } // no readable look-options: the ring-model's own exterior stands in

export function modeOf(looks: LookOptions | null, ring: RingModel | null): Mode {
  if (looks) {
    const options = shownOptions(looks)
    return options.length ? { kind: 'options', options } : { kind: 'none' }
  }
  const s = ring?.exterior.status
  return ring?.exterior.file && (s === 'in-design' || s === 'picked') ? { kind: 'fallback' } : { kind: 'none' }
}

export const sizeText = (b: { x: number; y: number; z: number }): string => [b.x, b.y, b.z].map((n) => Math.round(n * 10) / 10).join(' × ') + ' mm'

/** The short name of a screen state: its bundle label up to the first comma or bracket. */
export const shortLabel = (label: string): string => label.split(/[,(]/)[0]?.trim() || label

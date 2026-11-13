// Plain-word formats for sizes and dates. No locale calls: the same text on every machine.
const UNITS = ['B', 'KB', 'MB', 'GB'] as const
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] as const

/** 42075172 -> "40.1 MB"; under 10 of a unit keeps one decimal, above it none. */
export function formatSize(bytes: number): string {
  let v = bytes
  let u = 0
  while (v >= 1024 && u < UNITS.length - 1) {
    v /= 1024
    u += 1
  }
  const text = u === 0 || v >= 100 ? String(Math.round(v)) : v.toFixed(1).replace(/\.0$/, '')
  return `${text} ${UNITS[u]}`
}

/** "2026-11-10" or "2026-11-10T08:00:00Z" -> "10 Nov 2026"; anything else is returned as written. */
export function formatDay(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso)
  if (!m) return iso
  const month = MONTHS[Number(m[2]) - 1]
  return month ? `${Number(m[3])} ${month} ${m[1]}` : iso
}

export const baseName = (path: string): string => path.slice(path.lastIndexOf('/') + 1)
export const dirName = (path: string): string => (path.includes('/') ? path.slice(0, path.lastIndexOf('/')) : '')

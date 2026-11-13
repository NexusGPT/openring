// Pure helpers of the connection map. No ring value is written here: nodes, ends, signals and states are bundle values.
import type { Electronics } from '../../contract'

export type ConnectionMap = NonNullable<Electronics['connection_map']>
export type MapNode = ConnectionMap['nodes'][number]
export type Connection = ConnectionMap['connections'][number]

export interface Place {
  /** centre, percent of the map's width and height */
  x: number
  y: number
}
export interface Layout {
  places: ReadonlyMap<string, Place>
  /** the levels (rows) of the map, top to bottom */
  levels: number
  /** the most nodes on one level: sets the width of the map */
  across: number
}
export interface Edge {
  id: string
  a: string
  b: string
  /** index among the connections that join the same two nodes, and how many there are */
  k: number
  m: number
}

const pairKey = (a: string, b: string): string => (a < b ? `${a}\u0000${b}` : `${b}\u0000${a}`)

/** The connections as lines between nodes; those that join the same pair are numbered so they can be drawn side by side. */
export function edgesOf(map: ConnectionMap): Edge[] {
  const known = new Set(map.nodes.map((n) => n.id))
  const byPair = new Map<string, Connection[]>()
  for (const c of map.connections) {
    const [a, b] = c.ends
    if (!a || !b || !known.has(a.node) || !known.has(b.node)) continue
    const key = pairKey(a.node, b.node)
    byPair.set(key, [...(byPair.get(key) ?? []), c])
  }
  const out: Edge[] = []
  for (const list of byPair.values()) {
    list.forEach((c, k) => out.push({ id: c.id, a: c.ends[0].node, b: c.ends[1].node, k, m: list.length }))
  }
  return out
}

/** Levels (rows) by distance from the start of each connected part of the map; the start is an end of its longest chain (a node on the
 *  ring's side first), so the map reads from the ring outward. A part that does not touch the first one starts its own levels at the
 *  top. Inside a level, nodes stand near the average position of their neighbours on the level above. */
export function layoutNodes(map: ConnectionMap): Layout {
  const ids = map.nodes.map((n) => n.id)
  const adj = new Map<string, Set<string>>(ids.map((i) => [i, new Set<string>()]))
  for (const e of edgesOf(map)) {
    adj.get(e.a)?.add(e.b)
    adj.get(e.b)?.add(e.a)
  }
  const scopeOf = (i: string): string | null => map.nodes.find((n) => n.id === i)?.scope ?? null
  const bfs = (root: string): Map<string, number> => {
    const d = new Map<string, number>([[root, 0]])
    const queue = [root]
    while (queue.length > 0) {
      const cur = queue.shift() as string
      for (const n of adj.get(cur) ?? []) {
        if (d.has(n)) continue
        d.set(n, (d.get(cur) ?? 0) + 1)
        queue.push(n)
      }
    }
    return d
  }
  // the connected parts, the biggest first
  const seen = new Set<string>()
  const parts: string[][] = []
  for (const i of ids) {
    if (seen.has(i)) continue
    const members = [...bfs(i).keys()]
    members.forEach((m) => seen.add(m))
    parts.push(members.sort((p, q) => ids.indexOf(p) - ids.indexOf(q)))
  }
  parts.sort((p, q) => q.length - p.length)
  const depth = new Map<string, number>()
  for (const part of parts) {
    const ecc = new Map(part.map((i) => [i, Math.max(...bfs(i).values())] as const))
    const longest = Math.max(...ecc.values())
    const ends = part.filter((i) => ecc.get(i) === longest)
    ends.sort((p, q) => Number(scopeOf(p) === 'case') - Number(scopeOf(q) === 'case') || (adj.get(p)?.size ?? 0) - (adj.get(q)?.size ?? 0) || ids.indexOf(p) - ids.indexOf(q))
    for (const [i, d] of bfs(ends[0] as string)) depth.set(i, d)
  }
  const levels = Math.max(0, ...depth.values()) + 1
  const order: string[][] = Array.from({ length: levels }, (_, l) => ids.filter((i) => depth.get(i) === l))
  const across = Math.max(1, ...order.map((o) => o.length))
  const pos = new Map<string, number>() // 0..1 across the map
  const set = (row: string[]) => row.forEach((i, k) => pos.set(i, (k + 0.5 + (across - row.length) / 2) / across))
  order.forEach(set)
  const mean = (i: string, level: number): number | null => {
    const xs = [...(adj.get(i) ?? [])].filter((n) => (depth.get(n) ?? 0) < level).map((n) => pos.get(n) ?? 0.5)
    return xs.length ? xs.reduce((sum, x) => sum + x, 0) / xs.length : null
  }
  for (let l = 1; l < levels; l++) {
    order[l] = [...(order[l] ?? [])].sort((p, q) => (mean(p, l) ?? 0.5) - (mean(q, l) ?? 0.5) || ids.indexOf(p) - ids.indexOf(q))
    set(order[l] ?? [])
  }
  const places = new Map<string, Place>()
  for (const i of ids) places.set(i, { x: (pos.get(i) ?? 0.5) * 100, y: ((depth.get(i) ?? 0) + 0.5) / levels * 100 })
  return { places, levels, across }
}

/** Where a pill or a line end sits for the k-th of m parallel connections: the x shift, in percent of the map's width. */
export const shiftOf = (k: number, m: number, step = 3): number => (k - (m - 1) / 2) * step

export const nodeOf = (map: ConnectionMap, id: string): MapNode | null => map.nodes.find((n) => n.id === id) ?? null
export const nodeLabel = (map: ConnectionMap, id: string): string => nodeOf(map, id)?.label ?? id

/** Short words for a connection: the labels of its two nodes. */
export const titleOf = (map: ConnectionMap, c: Connection): string => `${nodeLabel(map, c.ends[0].node)} to ${nodeLabel(map, c.ends[1].node)}`

/** A joint is shown as open when no design file draws it: its cell says not drawn, or says it is stated in text only. */
export const isOpen = (c: Connection): boolean => c.drawn.state !== 'drawn'

/** The words for an open joint's state, by the kind of openness. */
export const openWords = (c: Connection): string => (c.drawn.state === 'text-only' ? 'Stated in text only: no design file draws it.' : 'Not drawn in any design file.')

/** "N of M conductors complete" from the conductor lines of the data, or null when the data has none for this joint. */
export const conductorWords = (c: Connection): string | null => (c.conductors ? `${c.conductors.complete} of ${c.conductors.total} conductors complete` : null)

/** The connections that end on the board of this group (a band circuit group holds all its ring sizes). */
export function connectionsOfBoard(map: ConnectionMap | null | undefined, group: string): Connection[] {
  if (!map) return []
  const nodes = new Set(map.nodes.filter((n) => n.board === group).map((n) => n.id))
  return map.connections.filter((c) => c.ends.some((e) => nodes.has(e.node)))
}

const fold = (s: string): string => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
/** Plain-text match of a typed word against a connection's id, ends, nets and carrier. */
export function matchesConnection(map: ConnectionMap, c: Connection, q: string): boolean {
  const t = fold(q.trim())
  if (!t) return true
  return [c.id, titleOf(map, c), c.signal, c.how.kind, c.how.text, ...c.ends.map((e) => e.text)].some((f) => fold(f).includes(t))
}

export type ConductorFile = NonNullable<ConnectionMap['conductor_file']>
export type Conductor = NonNullable<Connection['conductor_lines']>[number]
export type ConductorEnd = Conductor['first']

/** The count line for the whole product, from the conductor file record: "N of M conductors complete", or the words of why there is no count. */
export function productCountWords(f: ConductorFile | undefined): string {
  if (!f) return 'The conductor list is not in the data yet. Run npm run collect.'
  if (f.status !== 'ok') return f.note ?? `The conductor file is ${f.status}.`
  const none = f.no_conductor > 0 ? ` · ${f.no_conductor} ${f.no_conductor === 1 ? 'line' : 'lines'} without a conductor` : ''
  return `${f.complete} of ${f.total} conductors complete${none}`
}

/** What the conductor section of a connection says when it cannot simply list rows: the file's state, no line, or a count that differs. Null when the list stands. */
export function conductorProblem(c: Connection, f: ConductorFile | undefined): string | null {
  if (!f) return 'The conductor list is not in the data yet. Run npm run collect.'
  if (f.status !== 'ok') return f.note ?? `The conductor file is ${f.status}.`
  const n = c.conductor_lines?.length ?? 0
  if (n === 0) return c.no_conductor?.length ? null : 'No conductor line of the file names this connection.'
  if (c.conductors && c.conductors.total !== n) return `The list shows ${n} conductors; the count of this connection says ${c.conductors.total}.`
  return null
}

/** The ring sizes that any conductor of the connection gives a length for, in the order of the file. */
export const sizesOf = (c: Connection): string[] => [...new Set((c.conductor_lines ?? []).flatMap((k) => k.lengths.map((l) => l.size)))]

/** The lengths of one conductor for one ring size, as the file writes them (a copper length and a cut length may both be there). */
export const lengthsFor = (k: Conductor, size: string | null): Conductor['lengths'] => k.lengths.filter((l) => l.size === size)

/** Both signals when they differ, one when they are equal. */
export const signalWords = (k: Conductor): string => (k.signal_a === k.signal_b ? k.signal_a : `${k.signal_a} to ${k.signal_b}`)

/** A terminal in short: the part and its pin. */
export const terminalWords = (e: ConductorEnd): string => [e.part, e.pin].filter(Boolean).join(' ')

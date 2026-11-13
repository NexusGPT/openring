// The shell's stage: takes `scene` ({route, options}) from src/app/stage-scene and turns it into <Stage/> props
// from the data bundle. A new scene never remounts the stage and never reloads a model it already holds.
// Options a screen may set with useStageScene (all optional; see docs/lanes/stage.md):
//   show: 'exterior' | 'internals' | 'case' | 'looks'   preset, finish (name), screen (state id; null = off)
//   light, explode (0..1), isolatedLayer, lidOpen (deg)
// The selected part is the URL's ?part=<id>; a click on a part writes it.
import { useMemo } from 'react'
import { useSearchParams } from '../app/router'
import type { StageScene } from '../app/stage-scene'
import type { BannerSpec } from '../contract'
import { useRecord } from '../data'
import { Stage } from './Stage'
import type { StageProps, ViewPreset, ViewSpec } from './types'
import { VIEW_PRESETS } from './types'
import { caseView, internalsView, lookView, ringView } from './views'

/** The address after a pick: ?part=<id> for a node with a parts-list line, ?object=<node> for one without, none for empty space. */
export function pickParams(params: URLSearchParams, nodes: readonly { name: string; part_ids: string[] }[], pick: { node: string } | null): URLSearchParams {
  const next = new URLSearchParams(params)
  next.delete('part')
  next.delete('object')
  const id = pick ? nodes.find((n) => n.name === pick.node)?.part_ids[0] : null
  if (id) next.set('part', id)
  else if (pick) next.set('object', pick.node)
  return next
}

export function noticeFor(loading: boolean, status: string | undefined, file: string | undefined, views: number): BannerSpec | null {
  if (loading || views > 0) return null
  return status === 'unparsed' ? { kind: 'unparsed', file: file ?? 'ring-model.json' } : { kind: 'missing' }
}
/** Display names: the screen's `names` option (a JSON object node -> name), else the node name with spaces. */
function nameTable(names: unknown, ring: { nodes: readonly { name: string }[] } | null): Record<string, string> {
  try {
    if (typeof names === 'string') return JSON.parse(names) as Record<string, string>
  } catch {
    /* fall back to node names */
  }
  return Object.fromEntries((ring?.nodes ?? []).map((n) => [n.name, n.name.replace(/_/g, ' ')]))
}
const str = (v: unknown): string | null => (typeof v === 'string' ? v : null)
const num = (v: unknown): number | undefined => (typeof v === 'number' ? v : undefined)

export default function SceneStage({ scene }: { scene: StageScene }) {
  const ringRec = useRecord('ring-model')
  const ring = ringRec.state?.data ?? null
  const placements = useRecord('part-placements').state?.data ?? null
  const looks = useRecord('look-options').state?.data ?? null
  const caseRec = useRecord('case').state?.data ?? null
  const [params, setParams] = useSearchParams()
  const o = scene.options
  const show = str(o.show) ?? (scene.route === 'case' ? 'case' : 'exterior')

  const views = useMemo<ViewSpec[]>(() => {
    if (!ring) return []
    if (show === 'internals-only') return [internalsView(ring)] // the inside model alone (tests); screens use 'internals', which is the ring opened
    if (show === 'case') return caseRec && caseView(caseRec) ? [caseView(caseRec) as ViewSpec] : []
    const shown = show === 'looks' ? (looks?.options ?? []).filter((x) => !x.rejected && x.glb) : []
    return shown.length ? shown.map((x) => lookView(ring, x)) : [ringView(ring)]
  }, [ring, looks, caseRec, show])
  const lidded = views.map((v) => (v.lid ? { ...v, lid: { ...v.lid, openDeg: num(o.lidOpen) ?? 0 } } : v))

  const finish = looks?.finishes.find((f) => f.name === str(o.finish)) ?? looks?.finishes[0] ?? null
  const preset = VIEW_PRESETS.find((p) => p === o.preset) as ViewPreset | undefined
  const screenState = 'screen' in o ? str(o.screen) : (ring?.screens.states[0]?.state ?? null)
  const partId = params.get('part')
  const objectName = params.get('object')
  const selectedNode = (partId && ring?.nodes.find((n) => n.part_ids.includes(partId))?.name) || objectName || null

  const labels = useMemo(() => nameTable(o.names, ring), [o.names, ring])
  const props: StageProps = {
    views: lidded,
    notice: noticeFor(ringRec.loading, ringRec.state?.status, ringRec.state?.entry.source[0], lidded.length),
    ringModel: ring,
    placements,
    finish: finish ? { colour: finish.colour, roughness: finish.roughness } : null,
    screenState,
    lightOn: o.light === true,
    elapsedSec: num(o.elapsed),
    preset: preset ?? 'three-quarter',
    explode: num(o.explode) ?? 0,
    isolatedLayer: str(o.isolatedLayer),
    selectedNode,
    labels,
    route: scene.route,
    onPick: (pick) => setParams(pickParams(params, ring?.nodes ?? [], pick)),
  }
  return <Stage {...props} />
}

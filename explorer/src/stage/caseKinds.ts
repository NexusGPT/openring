// A default material class for the nodes of the case model, from the shape of their names (the case record
// lists node names and part ids, no kinds). First match wins; anything else is polymer. The outer shell and the lid are
// satin metal and the ring's seat is dark soft-touch, so the case reads as an object and not as one grey block. A collector that
// writes kinds for the case nodes replaces this map.
import type { Kind } from '../contract'
import type { MaterialClass } from './classMaterials'
import { KIND_CLASS } from './classMaterials'
import type { NodeSpec } from './types'

const RULES: ReadonlyArray<[RegExp, MaterialClass]> = [
  [/holder|glide|foot|feet|gasket|seal/i, 'polymer'], // moulded holders, the feet under the case
  [/window|diffus/i, 'resin'],
  [/^led/i, 'resin'],
  [/board|pcb/i, 'pcb'],
  [/^pin_p\d|contact|pad/i, 'gold'], // the contact pins
  [/magnet|hinge|pivot|spring|screw|pin/i, 'metal'],
  [/cell|batter/i, 'cell'],
  [/^[ujlqxy]\d/i, 'chip'], // reference-designator nodes: chips, connectors, coils
  [/shell|lid|housing|base|cover/i, 'satin'], // what the hand holds: satin metal
  [/post|tray|insert|cradle|liner|seat|well/i, 'soft'], // where the ring rests: dark soft-touch
]

const KIND_OF: Partial<Record<MaterialClass, Kind>> = { metal: 'finish metal', gold: 'gold', polymer: 'matte', resin: 'light', glass: 'glass', screen: 'screen', satin: 'satin', soft: 'matte' }

export function caseClass(name: string): MaterialClass {
  return RULES.find(([re]) => re.test(name))?.[1] ?? 'polymer'
}

export function caseNodeSpecs(nodes: readonly { name: string }[]): NodeSpec[] {
  return nodes.map((n) => {
    const materialClass = caseClass(n.name)
    return { name: n.name, kind: KIND_OF[materialClass] ?? 'plain', materialClass }
  })
}

export { KIND_CLASS }

// The test API of the 3D stage, frozen here. The stage lane implements it on window.__stage; every
// check and journey reads only these members. A change is a change of the contract.
export interface Box3 {
  min: [number, number, number]
  max: [number, number, number]
}

export interface StageApi {
  /** true once the first model is loaded and a frame has rendered */
  ready: boolean
  /** WebGL contexts created in this page; the shell keeps it at 1 across routes */
  contexts: number
  /** frames rendered so far */
  frames: number
  /** false after the first drag */
  autoRotate: boolean
  azimuthDeg(): number
  /** nodes of the loaded model that have no entry in the bundle's node-to-kind map; [] when all are mapped */
  unmappedNodes(): string[]
  /** bounding box per layer id, in mm */
  layerBoxes(): Record<string, Box3>
  /** pixel position of a node's centre in the canvas, for clicks */
  screenPos(nodeName: string): { x: number; y: number } | null
  isolatedLayer(): string | null
  /** colour (css hex) of a node of one option's model */
  material(option: string, node: string): { color: string } | null
  fingerVisible(option: string): boolean
  lightOn(): boolean
  /** labels of the fields drawn on the lit screen face now */
  screenFields(): string[]
  nodeRotationDeg(node: string): number
  /** renderer clear colour and alpha: the canvas is transparent over the page background */
  clearColor(): { colour: string; alpha: number }
  /** the exterior on the stage: picked, in-design (a model not approved yet) or none (plain slab); null when no exterior view */
  exteriorState(): 'picked' | 'in-design' | 'none' | null
  /** projected box of the object and its shadow in one view, as shares of the view (0..1, y down); the stage keeps it 12 % inside */
  fitBox(option: string): { left: number; right: number; top: number; bottom: number } | null
  /** opacity of the exterior shell (1 closed .. 0 open) in the first view that has one; null otherwise */
  exteriorOpacity(): number | null
  /** opacity of one part of the inside model now (1 solid, about 0.12 ghost); null when unknown */
  partOpacity(node: string): number | null
  /** node whose outline is drawn (and how strong, 0..1) */
  outline(): { node: string; strength: number } | null
  /** distance of the first view's camera from its target, mm */
  cameraDistance(): number
  /** current view preset: three-quarter, top, side or finger */
  preset(): string
  /** explode value now, 0 assembled .. 1 fully opened */
  explode(): number
}

declare global {
  interface Window {
    __stage?: StageApi
  }
}

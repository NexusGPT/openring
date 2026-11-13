// Dev-only harness page for the stage. Not part of the app build. Modes by query: ?mode=
//   assembled (default) | exploded | slab | compare | fail ; &screen=rec|idle|off ; &preset=top|side|finger
// window.__harness.set({...}) changes any prop from a script.
import { createRoot } from 'react-dom/client'
import { useEffect, useState } from 'react'
import { caseView, internalsView, exteriorView, ringView } from './views'
import { Stage, type StageProps, VIEW_PRESETS } from './index'
import { REAL_LAYERS, EXTERIOR_NODES, FINISH, FINISH_ALT, PLACEMENTS, RING, brokenSpec, exteriorSpec, internalsSpec, slabSpec } from './__tests__/harness-data'

const q = new URLSearchParams(location.search)
const mode = q.get('mode') ?? 'assembled'

function initial(): StageProps {
  const base: StageProps = { views: [exteriorSpec()], ringModel: RING, placements: PLACEMENTS, finish: FINISH, screenState: q.get('screen') ?? 'rec', preset: (q.get('preset') as StageProps['preset']) ?? 'three-quarter', route: 'look' }
  if (mode === 'exploded') return { ...base, views: [internalsSpec()], explode: 1, screenState: null }
  if (mode === 'slab') return { ...base, views: [slabSpec()] }
  if (mode === 'compare') return { ...base, views: [{ ...exteriorSpec('a'), label: 'Option A' }, { ...exteriorSpec('b'), label: 'Option B' }] }
  if (mode === 'lid') return { ...base, views: [{ ...exteriorSpec('lid'), lid: { node: 'button', point: { x: -6, y: -7, z: 2 }, axis: { x: 1, y: 0, z: 0 }, openDeg: 40 } }] }
  if (mode === 'fail') return { ...base, views: [brokenSpec()] }
  return base
}

function Harness() {
  const [props, setProps] = useState<StageProps>(initial)
  useEffect(() => {
    if (mode === 'real-case') {
      void Promise.all([fetch('/data/ring-model.json').then((r) => r.json()), fetch('/data/case/index.json').then((r) => r.json())]).then(([ring, c]) => {
        const v = caseView(c)
        setProps((st) => ({ ...st, ringModel: ring, views: v ? [{ ...v, lid: v.lid ? { ...v.lid, openDeg: Number(q.get('open') ?? 0) } : undefined }] : [], screenState: null }))
      })
      return
    }
    if (!mode.startsWith('real')) return
    void Promise.all([fetch('/data/ring-model.json').then((r) => r.json()), fetch('/data/placements.json').then((r) => (r.ok ? r.json() : REAL_LAYERS)).catch(() => REAL_LAYERS)]).then(([ring, placements]) => {
      const inside = mode !== 'real-exterior' && mode !== 'real-ring'
      setProps((s) => ({ ...s, ringModel: ring, placements, views: [mode === 'real-ring' ? ringView(ring) : inside ? internalsView(ring) : exteriorView(ring)], explode: mode === 'real-exploded' || mode === 'real-isolated' ? 1 : 0, isolatedLayer: mode === 'real-isolated' ? q.get('layer') : null, screenState: null }))
    })
  }, [])
  useEffect(() => {
    ;(window as unknown as { __harness: unknown }).__harness = { set: (p: Partial<StageProps>) => setProps((s) => ({ ...s, ...p })), ring: RING, placements: PLACEMENTS, nodes: EXTERIOR_NODES, views: props.views }
  }, [])
  const set = (p: Partial<StageProps>) => setProps((s) => ({ ...s, ...p }))
  const [picked, setPicked] = useState<string>('')
  return (
    <>
      <div className="bar">
        <span>screen</span>
        {[...RING.screens.states.map((s) => s.state), 'off'].map((s) => (
          <button key={s} className={(props.screenState ?? 'off') === s ? 'on' : ''} onClick={() => set({ screenState: s === 'off' ? null : s })}>{s}</button>
        ))}
        <span>view</span>
        {VIEW_PRESETS.map((p) => (
          <button key={p} className={props.preset === p ? 'on' : ''} onClick={() => set({ preset: p })}>{p}</button>
        ))}
        <span>finish</span>
        <button onClick={() => set({ finish: FINISH })}>dark</button>
        <button onClick={() => set({ finish: FINISH_ALT })}>gold</button>
        <label>explode <input type="range" min="0" max="1" step="0.01" value={props.explode ?? 0} onChange={(e) => set({ explode: Number(e.target.value) })} /></label>
        <label><input type="checkbox" checked={!!props.lightOn} onChange={(e) => set({ lightOn: e.target.checked })} /> light</label>
        <span data-testid="harness.picked">{picked}</span>
      </div>
      <div className="stage">
        <Stage {...props} selectedNode={picked || null} onPick={(p) => setPicked(p?.node ?? '')} />
      </div>
    </>
  )
}

createRoot(document.getElementById('root') as HTMLElement).render(<Harness />)

// The persistent stage slot. It lives in the shell, outside the routes, so it is mounted once and never
// again: a route change does not touch it. The stage piece (src/stage/index.tsx, default export `Stage`,
// prop `scene: StageScene`) is picked up by glob; until it lands the slot shows a quiet label.
import { Suspense, lazy, useId, type ComponentType } from 'react'
import { testId } from '../contract'
import { useStageSceneValue, type StageScene } from './stage-scene'

type StageComponent = ComponentType<{ scene: StageScene }>
const loaders = import.meta.glob<Record<string, unknown>>('../stage/index.tsx')
const [loader] = Object.values(loaders)

const Stage = loader
  ? lazy(async () => {
      const m = await loader()
      const c = m.default ?? m.Stage
      if (typeof c === 'function') return { default: c as StageComponent }
      return { default: StageMissing }
    })
  : null

function StageMissing() {
  return (
    <div className="stage-empty" data-testid={testId('app', 'stage-placeholder')}>
      <span className="label">Stage not built yet</span>
    </div>
  )
}

export function StageHost() {
  const id = useId()
  const scene = useStageSceneValue()
  const Body = Stage ?? StageMissing
  return (
    <div className="stage" data-stage-id={id} data-testid={testId('app', 'stage')}>
      <Suspense fallback={null}>
        <Body scene={scene} />
      </Suspense>
    </div>
  )
}

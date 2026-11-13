// What a screen asks of the persistent stage. The shell owns ONE stage for the whole session; a screen
// never mounts its own. A screen states its wish with useStageScene(options); the stage reads `scene`.
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { RouteId } from '../contract'

/** Free-form wishes of the current screen (for example a view preset or an isolated layer id). The
 *  keys and values are agreed between a screen and the stage; the shell only carries them. */
export type StageOptions = Readonly<Record<string, string | number | boolean | null>>

export interface StageScene {
  /** the route on screen now */
  route: RouteId
  options: StageOptions
}

interface Ctx {
  options: StageOptions
  setOptions(o: StageOptions): void
}
const SceneContext = createContext<Ctx | null>(null)
const NONE: StageOptions = {}

export function StageSceneProvider({ route, children }: { route: RouteId; children: ReactNode }) {
  const [options, setOptions] = useState<StageOptions>(NONE)
  const value = useMemo(() => ({ options, setOptions }), [options])
  return (
    <SceneContext.Provider value={value}>
      <RouteScene route={route}>{children}</RouteScene>
    </SceneContext.Provider>
  )
}

const RouteContext = createContext<RouteId>('home')
function RouteScene({ route, children }: { route: RouteId; children: ReactNode }) {
  return <RouteContext.Provider value={route}>{children}</RouteContext.Provider>
}

/** The scene the stage should draw now. */
export function useStageSceneValue(): StageScene {
  const ctx = useContext(SceneContext)
  const route = useContext(RouteContext)
  return useMemo(() => ({ route, options: ctx?.options ?? NONE }), [route, ctx?.options])
}

/** A screen calls this to steer the stage; its wishes are dropped when the screen unmounts. */
export function useStageScene(options: StageOptions): void {
  const ctx = useContext(SceneContext)
  const key = JSON.stringify(options)
  const set = ctx?.setOptions
  useEffect(() => {
    set?.(JSON.parse(key) as StageOptions)
    return () => set?.(NONE)
  }, [key, set])
}

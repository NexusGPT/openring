// The route registry. Screen entries are found by import.meta.glob over src/routes/*/index.tsx: a screen
// piece that has not landed yet is simply absent, and its route shows the honest placeholder.
import { lazy, type ComponentType, type LazyExoticComponent } from 'react'
import { ROUTES, type RouteId } from '../contract'
import { ScreenPlaceholder } from './ScreenPlaceholder'
export { FILES_HASH, FILES_TO, ROUTE_PATH, TAB_LABEL, routeOfPath, isKnownPath } from './route-names'

/** The one folder whose name differs from its route id. */
const FOLDER_ROUTE: Record<string, RouteId> = { 'open-files': 'open' }

type Mod = Record<string, unknown>
const loaders = import.meta.glob<Mod>('../routes/*/index.tsx')

function routeOfFolder(file: string): RouteId | null {
  const folder = file.split('/').slice(-2, -1)[0] ?? ''
  const id = FOLDER_ROUTE[folder] ?? folder
  return (ROUTES as readonly string[]).includes(id) ? (id as RouteId) : null
}

function componentOf(m: Mod): ComponentType | null {
  const c = m.default ?? m.Screen
  return typeof c === 'function' ? (c as ComponentType) : null
}

export type Screen = LazyExoticComponent<ComponentType>
const SCREENS: Partial<Record<RouteId, Screen>> = {}
for (const [file, load] of Object.entries(loaders)) {
  const id = routeOfFolder(file)
  if (!id) continue
  SCREENS[id] = lazy(async () => {
    const c = componentOf(await load())
    if (c) return { default: c }
    return { default: ScreenPlaceholder }
  })
}

/** The screen of a route, or null while its piece has not landed. */
export function screenFor(id: RouteId): Screen | null {
  return SCREENS[id] ?? null
}

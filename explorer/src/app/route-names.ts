// Route names, paths and the path-to-route rule. Pure data; no screen is imported here.
import { ROUTES, type RouteId } from '../contract'

export const TAB_LABEL: Record<RouteId, string> = {
  home: 'Home',
  look: 'Look',
  inside: 'Inside',
  electronics: 'Electronics',
  board: 'Board',
  parts: 'Parts',
  behaviour: 'Behaviour',
  case: 'Case',
  open: 'Open items',
}

export const ROUTE_PATH: Record<RouteId, string> = Object.fromEntries(
  ROUTES.map((r) => [r, r === 'home' ? '/' : `/${r}`]),
) as Record<RouteId, string>

/** The files section of screen 9, reached from the Files entry of the bar. */
export const FILES_HASH = '#files'
export const FILES_TO = `${ROUTE_PATH.open}${FILES_HASH}`

export function routeOfPath(pathname: string): RouteId {
  const first = pathname.replace(/^\/+/, '').split('/')[0] ?? ''
  return (ROUTES as readonly string[]).includes(first) ? (first as RouteId) : 'home'
}


/** True for '/' and for the path of one of the 9 screens (with anything below it). */
export function isKnownPath(pathname: string): boolean {
  const first = pathname.replace(/^\/+/, '').split('/')[0] ?? ''
  return first === '' || (ROUTES as readonly string[]).includes(first)
}

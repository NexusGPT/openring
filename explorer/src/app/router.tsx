// A small history router. react-router writes the literal address of a local host into every build that
// contains it, and the hosted-build check (CONTRACT section 10) fails on that string; this module has
// the four things the app needs and nothing else. Screens import Link, useLocation, useNavigate and
// useSearchParams from here, with the names and shapes they have in react-router-dom.
import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
  type AnchorHTMLAttributes, type MouseEvent, type ReactNode,
} from 'react'

export interface Location {
  pathname: string
  search: string
  hash: string
}
export interface NavigateOptions {
  replace?: boolean
}
interface Ctx {
  location: Location
  basename: string
  navigate(to: string, opts?: NavigateOptions): void
}
const RouterContext = createContext<Ctx | null>(null)

function useCtx(): Ctx {
  const c = useContext(RouterContext)
  if (!c) throw new Error('Router is missing above this component')
  return c
}

/** Split '/a/b?x=1#h' into its three parts. */
export function parseTo(to: string): Location {
  const hashAt = to.indexOf('#')
  const hash = hashAt >= 0 ? to.slice(hashAt) : ''
  const rest = hashAt >= 0 ? to.slice(0, hashAt) : to
  const qAt = rest.indexOf('?')
  return { pathname: (qAt >= 0 ? rest.slice(0, qAt) : rest) || '/', search: qAt >= 0 ? rest.slice(qAt) : '', hash }
}

/** The location of the browser address bar, relative to the app's basename. */
export function readWindow(basename: string, w: Pick<Window, 'location'> = window): Location {
  const { pathname, search, hash } = w.location
  const rel = basename && pathname.startsWith(basename) ? pathname.slice(basename.length) : pathname
  return { pathname: rel || '/', search, hash }
}

/** basename: '' at the root of a host, '/ring' under a sub-path. memory: keep the location in state only
 *  (tests); the value is the starting path. */
export function Router({ basename = '', memory, children }: { basename?: string; memory?: string; children: ReactNode }) {
  const [location, setLocation] = useState<Location>(() => (memory !== undefined ? parseTo(memory) : readWindow(basename)))

  useEffect(() => {
    if (memory !== undefined) return
    const onPop = () => setLocation(readWindow(basename))
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [basename, memory])

  const navigate = useCallback(
    (to: string, opts?: NavigateOptions) => {
      const next = parseTo(to)
      if (memory === undefined) {
        const url = `${basename}${next.pathname}${next.search}${next.hash}`
        if (opts?.replace) window.history.replaceState(null, '', url)
        else window.history.pushState(null, '', url)
      }
      setLocation(next)
    },
    [basename, memory],
  )
  const value = useMemo(() => ({ location, basename, navigate }), [location, basename, navigate])
  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>
}

export function useLocation(): Location {
  return useCtx().location
}
export function useNavigate(): (to: string, opts?: NavigateOptions) => void {
  return useCtx().navigate
}

/** The query string as URLSearchParams, and a setter that writes it back into the address. */
export function useSearchParams(): [URLSearchParams, (next: URLSearchParams | Record<string, string>, opts?: NavigateOptions) => void] {
  const { location, navigate } = useCtx()
  const params = useMemo(() => new URLSearchParams(location.search), [location.search])
  const set = useCallback(
    (next: URLSearchParams | Record<string, string>, opts?: NavigateOptions) => {
      const q = new URLSearchParams(next).toString()
      navigate(`${location.pathname}${q ? `?${q}` : ''}${location.hash}`, opts)
    },
    [location.pathname, location.hash, navigate],
  )
  return [params, set]
}

type LinkProps = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> & { to: string; replace?: boolean }

/** An anchor that navigates without a page load; a modified click or a new-tab target is left to the browser. */
export function Link({ to, replace, onClick, target, ...rest }: LinkProps) {
  const { navigate, basename } = useCtx()
  const click = (e: MouseEvent<HTMLAnchorElement>) => {
    onClick?.(e)
    if (e.defaultPrevented || e.button !== 0 || (target && target !== '_self') || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return
    e.preventDefault()
    navigate(to, { replace })
  }
  return <a {...rest} target={target} href={`${basename}${to}`} onClick={click} />
}

/** Render nothing and move to `to` (replacing the entry); for an unknown path. */
export function Redirect({ to }: { to: string }) {
  const navigate = useNavigate()
  useEffect(() => navigate(to, { replace: true }), [navigate, to])
  return null
}

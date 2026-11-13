import { Suspense, useEffect, useState } from 'react'
import { testId, type RouteId } from '../contract'
import { Redirect, useLocation } from './router'
import { ErrorBoundary } from './ErrorBoundary'
import { ScreenPlaceholder } from './ScreenPlaceholder'
import { StageHost } from './StageHost'
import { StageSceneProvider } from './stage-scene'
import { TabBar } from './TabBar'
import { TAB_LABEL, isKnownPath, routeOfPath, screenFor } from './routes'

function ExpandIcon({ open }: { open: boolean }) {
  // two chevrons: left when the panel can grow over the stage, right when it can shrink back
  const d = open ? 'M5 3 L9 7 L5 11 M13 3 L17 7 L13 11' : 'M9 3 L5 7 L9 11 M17 3 L13 7 L17 11'
  return (
    <svg width="22" height="14" viewBox="0 0 22 14" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      <path d={d} />
    </svg>
  )
}

function ScreenOf({ id }: { id: RouteId }) {
  const Screen = screenFor(id)
  return Screen ? <Screen /> : <ScreenPlaceholder />
}

/** The L1 Stage frame. Tab bar on top; stage on the left, mounted once; the area panel on the right.
 *  A route renders only into the panel. */
export function Shell() {
  const { pathname } = useLocation()
  const route = routeOfPath(pathname)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => setExpanded(false), [pathname])
  useEffect(() => {
    document.title = `Ring Explorer · ${TAB_LABEL[route]}`
  }, [route])
  useEffect(() => {
    if (!expanded) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setExpanded(false)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [expanded])

  return (
    <StageSceneProvider route={route}>
      <div className="app" data-testid={testId('app', 'shell')}>
        <TabBar />
        <main className="main" data-expanded={String(expanded)}>
          <StageHost />
          <div className="panel-cell">
            <section className="panel" aria-label={TAB_LABEL[route]} data-testid={testId('app', 'panel')}>
              <div className="panel-head">
                <button
                  type="button"
                  className="panel-expand"
                  data-testid={testId('app', 'panel-expand')}
                  aria-pressed={expanded}
                  aria-label={expanded ? 'Collapse the panel (Escape)' : 'Expand the panel over the stage'}
                  title={expanded ? 'Collapse (Escape)' : 'Expand'}
                  onClick={() => setExpanded((v) => !v)}
                >
                  <ExpandIcon open={expanded} />
                </button>
              </div>
              <div className="panel-body" data-testid={testId('app', 'panel-body')}>
                <ErrorBoundary key={route}>
                  <Suspense fallback={null}>
                    {isKnownPath(pathname) ? <ScreenOf id={route} /> : <Redirect to="/" />}
                  </Suspense>
                </ErrorBoundary>
              </div>
            </section>
          </div>
        </main>
      </div>
    </StageSceneProvider>
  )
}

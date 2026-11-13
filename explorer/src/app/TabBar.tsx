import { Link, useLocation } from './router'
import { ROUTES, testId } from '../contract'
import { FILES_HASH, FILES_TO, ROUTE_PATH, TAB_LABEL, routeOfPath } from './routes'
import { FreshnessStamp } from './FreshnessStamp'

/** The 56 px bar: brand, the 9 screens, the Files entry, the freshness stamp. */
export function TabBar() {
  const { pathname, hash } = useLocation()
  const current = routeOfPath(pathname)
  const onFiles = current === 'open' && hash === FILES_HASH
  return (
    <nav className="tabs" aria-label="Screens" data-testid={testId('app', 'tab-bar')}>
      <Link to="/" className="brand" data-testid={testId('app', 'brand')}>
        Ring Explorer
      </Link>
      {ROUTES.map((id) => {
        const active = id === current && !(id === 'open' && onFiles)
        return (
          <Link
            key={id}
            to={ROUTE_PATH[id]}
            className="tab"
            data-testid={testId('app', `tab-${id}`)}
            aria-current={active ? 'page' : undefined}
          >
            {TAB_LABEL[id]}
          </Link>
        )
      })}
      <span className="tabs-gap" />
      <Link
        to={FILES_TO}
        className="tab"
        data-testid={testId('app', 'tab-files')}
        aria-current={onFiles ? 'page' : undefined}
      >
        Files
      </Link>
      <FreshnessStamp />
    </nav>
  )
}

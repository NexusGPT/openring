import { useLocation } from './router'
import { testId } from '../contract'
import { TAB_LABEL, routeOfPath } from './route-names'

/** Shown while a screen's piece has not landed. A sentence the shell owns; data states use the contract's banners. */
export function ScreenPlaceholder() {
  const id = routeOfPath(useLocation().pathname)
  return (
    <div className="placeholder" role="status" data-testid={testId('app', 'screen-placeholder')} data-route={id}>
      <p className="label">{TAB_LABEL[id]}</p>
      <h1 className="display">Screen not built yet.</h1>
      <p className="muted">This screen arrives with the next piece of the build.</p>
    </div>
  )
}

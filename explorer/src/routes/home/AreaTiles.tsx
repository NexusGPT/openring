import { StatePill, testId, type AreaStates } from '../../contract'
import { Link } from '../../app/router'
import { ROUTE_PATH, TAB_LABEL } from '../../app/route-names'
import { banner } from '../../contract'
import type { RecordState } from '../../data'

/** The 8 areas: name, state pill and what is open; one click goes to the area. */
export function AreaTiles({ rec }: { rec: RecordState<AreaStates> }) {
  return (
    <div className="tiles">
      {rec.data?.areas.map((a) => {
        const stale = a.stale && a.basis_version && a.current_version
        const staleLine = stale ? banner({ kind: 'stale', basis: a.basis_version ?? '', current: a.current_version ?? '' }).sentence : null
        return (
          <Link key={a.id} to={ROUTE_PATH[a.id]} className="tile" data-testid={testId('home', 'area-tile')} data-area={a.id} title={a.why ?? undefined}>
            <span className="tile-head">
              <span className="tile-name">{TAB_LABEL[a.id]}</span>
              <StatePill route="home" state={a.state} />
            </span>
            {a.why ? (
              <span className="tile-why" data-dimmed={stale ? 'true' : undefined}>
                {a.why}
              </span>
            ) : null}
            {staleLine ? <span className="tile-stale label" title={staleLine}>{staleLine}</span> : null}
          </Link>
        )
      })}
    </div>
  )
}

// The connections that end on the shown board; each opens in Electronics. (A band circuit group lists its connections for every ring size.)
import { Link } from '../../app/router'
import { testId } from '../../contract'
import { connectionsOfBoard, isOpen, nodeLabel, type ConnectionMap } from '../../components/wiring/wiringModel'

export function ConnectionsOfBoard({ map, group }: { map: ConnectionMap | null; group: string }) {
  const list = connectionsOfBoard(map, group)
  if (!map || list.length === 0) return null
  return (
    <section className="bd-conns" aria-labelledby="bd-conns-h" data-testid={testId('board', 'connections')}>
      <h2 className="label" id="bd-conns-h">{`Connections on this board · ${list.length}`}</h2>
      <ul>
        {list.map((c) => (
          <li key={c.id}>
            <Link to={`/electronics?conn=${encodeURIComponent(c.id)}`} data-testid={testId('board', 'connection-link')} data-conn={c.id} data-open={isOpen(c) || undefined}>
              <span className="bd-ref">{c.id}</span>
              <span className="bd-name">{`${nodeLabel(map, c.ends[0].node)} to ${nodeLabel(map, c.ends[1].node)}`}</span>
              <span className="label">{isOpen(c) ? 'not drawn' : c.how.kind}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}

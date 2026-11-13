import { testId } from '../../contract'
import { Link } from '../../app/router'
import { ROUTE_PATH } from '../../app/route-names'
import { WORDS } from '../../contract'
import type { NextItem } from './model'

export function NextUp({ items, quiet }: { items: NextItem[]; quiet: boolean }) {
  if (!items.length) return quiet ? <p className="muted next-empty">{WORDS.nothingWaiting}</p> : null
  return (
    <ol className="next">
      {items.map((n) => {
        const inner = (
          <>
            <span className="next-title">{n.title}</span>
            <span className="next-line">{n.line}</span>
          </>
        )
        return (
          <li key={n.key} data-testid={testId('home', 'next-item')}>
            {n.to ? (
              <Link to={ROUTE_PATH[n.to]} className="next-link">
                {inner}
              </Link>
            ) : (
              <div className="next-link">{inner}</div>
            )}
          </li>
        )
      })}
    </ol>
  )
}

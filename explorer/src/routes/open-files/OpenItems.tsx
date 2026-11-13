// The open items: four groups, five chips, and for the supplier chip one more row of chips, one per
// supplier. A filter that leaves nothing says "nothing waiting".
import { useMemo, useState } from 'react'
import { testId, type Files, type OpenItems as OpenData } from '../../contract'
import type { RecordState } from '../../data'
import { Collapse } from './Disclosure'
import { ItemRow } from './ItemRow'
import { FILTERS, OPEN_WORDS, applyFilter, countOf, groupsOf, suppliersOf, type FilterId, type Row } from './model'

const SHOWN = 5
/** More suppliers than this and a chip per supplier is clutter: the rows already name who. */
const WHO_CHIPS_MAX = 6

/** The first rows of a group; in the all view the rest wait behind "Show N more" (still in the page). */
function GroupRows({ rows, files, clamp }: { rows: Row[]; files: RecordState<Files> | null; clamp: boolean }) {
  const [more, setMore] = useState(false)
  const head = clamp ? rows.slice(0, SHOWN) : rows
  const rest = clamp ? rows.slice(SHOWN) : []
  const li = (r: Row) => <ItemRow key={`${r.group}:${r.id}`} row={r} files={files} />
  return (
    <>
      <ul className="items">{head.map(li)}</ul>
      {rest.length ? (
        <>
          <Collapse open={more}>
            <ul className="items items-rest">{rest.map(li)}</ul>
          </Collapse>
          <button type="button" className="more" aria-expanded={more} data-testid={testId('open', 'show-more')} onClick={() => setMore(!more)}>
            {more ? 'Show fewer' : `Show ${rest.length} more`}
          </button>
        </>
      ) : null}
    </>
  )
}

export function OpenItems({ data, files }: { data: OpenData; files: RecordState<Files> | null }) {
  const [filter, setFilter] = useState<FilterId>('all')
  const [who, setWho] = useState<string | null>(null)
  const all = useMemo(() => groupsOf(data), [data])
  const suppliers = useMemo(() => suppliersOf(all), [all])
  const shown = applyFilter(all, filter, who)
  const rows = shown.reduce((n, g) => n + g.rows.length, 0)
  const pick = (id: FilterId) => {
    setFilter(id)
    setWho(null)
  }
  return (
    <div className="open-items">
      <div className="chips" role="group" aria-label="Show">
        {FILTERS.map((f) => (
          <button key={f.id} type="button" className="chip" aria-pressed={filter === f.id} data-filter={f.id} data-testid={testId('open', 'filter-chip')} onClick={() => pick(f.id)}>
            {f.label}
            <span className="chip-n">{countOf(all, f.id)}</span>
          </button>
        ))}
      </div>
      {filter === 'supplier' && suppliers.length > 1 && suppliers.length <= WHO_CHIPS_MAX ? (
        <div className="chips chips-who" role="group" aria-label="Who must act">
          {[null, ...suppliers].map((s) => (
            <button key={s ?? '*'} type="button" className="chip chip-sm" aria-pressed={who === s} data-testid={testId('open', 'who-chip')} onClick={() => setWho(s)}>
              {s ?? OPEN_WORDS.everyone}
            </button>
          ))}
        </div>
      ) : null}
      <div className="groups" key={`${filter}|${who ?? ''}`}>
        {shown.filter((g) => filter === 'all' || g.rows.length > 0).map((g) => (
          <section key={g.id} className="group" aria-labelledby={`og-${g.id}`} data-group={g.id}>
            <h3 className="label group-heading" id={`og-${g.id}`} data-testid={testId('open', 'group-heading')}>
              {g.title}
              <span className="group-n">{g.rows.length}</span>
            </h3>
            {g.rows.length ? (
              <GroupRows rows={g.rows} files={files} clamp={filter === 'all'} />
            ) : filter === 'all' ? (
              <p className="quiet">{OPEN_WORDS.nothingHere}</p>
            ) : null}
          </section>
        ))}
        {rows === 0 ? <p className="quiet nothing" role="status" data-testid={testId('open', 'nothing')}>{OPEN_WORDS.nothing}</p> : null}
      </div>
    </div>
  )
}

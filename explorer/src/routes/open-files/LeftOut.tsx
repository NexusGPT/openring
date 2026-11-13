// What a shared copy of the project does not carry (files record `left_out`): the group, how many files, and
// why, so a reader knows what to ask the owner for. Nothing is drawn on the owner's own machine.
import { testId, type Files } from '../../contract'

const WORDS = { title: 'Not in this copy', one: 'file', many: 'files' } as const

export function LeftOut({ items }: { items: NonNullable<Files['left_out']> }) {
  if (!items.length) return null
  return (
    <div className="left-out" data-testid={testId('open', 'left-out')}>
      <p className="label">{WORDS.title}</p>
      <ul>
        {items.map((i) => (
          <li key={i.what} data-testid={testId('open', 'left-out-row')}>
            <span className="lo-what">{i.what}</span>
            <span className="lo-count label">{i.count} {i.count === 1 ? WORDS.one : WORDS.many}</span>
            <span className="lo-why">{i.why}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

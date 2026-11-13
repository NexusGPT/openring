// One exterior option: title, one sentence, what it is worse at, and a Details disclosure. All words come from the bundle.
import { testId } from '../../contract'
import { LOOK_WORDS, sizeText, type LookOption } from './model'

export function OptionPanel({ option, picked }: { option: LookOption; picked: boolean }) {
  return (
    <article className="opt" data-testid={testId('look', 'look-option')} data-option={option.id} data-picked={picked ? 'true' : 'false'}>
      <header className="opt-head">
        <h3 className="opt-title">{option.title}</h3>
        {picked ? <span className="label opt-picked">{LOOK_WORDS.picked}</span> : null}
      </header>
      {option.sentence ? <p className="opt-line">{option.sentence}</p> : null}
      {option.worse_at.length ? (
        <div className="opt-worse">
          <span className="label">{LOOK_WORDS.worseAt}</span>
          <ul>
            {option.worse_at.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <details className="opt-details">
        <summary>{LOOK_WORDS.details}</summary>
        <dl>
          <dt className="label">{LOOK_WORDS.source}</dt>
          <dd>
            {option.source.file}
            {option.source.line ? `:${option.source.line}` : ''}
          </dd>
          {option.glb ? (
            <>
              <dt className="label">Bounds</dt>
              <dd>{sizeText(option.glb.bounds_mm)}</dd>
            </>
          ) : null}
        </dl>
      </details>
    </article>
  )
}

import { testId, type Case } from '../../contract'
import { WORDS } from './model'

/** What the model is made from and, when a design file says one, the sentence about the case's refit. Both come from the data. */
export function Honest({ model, refit }: { model: Case['model']; refit: Case['refit'] }) {
  if (!model && !refit) return null
  return (
    <section className="cs-sec cs-honest" data-testid={testId('case', 'honest')}>
      {model ? (
        <p className="cs-hint" data-testid={testId('case', 'model-source')}>
          <span className="label">{WORDS.model}</span>{' '}
          {`${model.file}, file time ${model.time}`}
        </p>
      ) : null}
      {refit ? (
        <p className="cs-hint cs-refit" data-testid={testId('case', 'refit')}>
          <span className="label">{WORDS.refit}</span>{' '}
          {refit.text}{' '}
          <span className="cs-refit-src">{`(${refit.source.file}${refit.source.line === null ? '' : `, line ${refit.source.line}`})`}</span>
        </p>
      ) : null}
    </section>
  )
}

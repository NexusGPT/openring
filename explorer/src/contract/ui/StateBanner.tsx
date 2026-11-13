import { bannerText, banner, type BannerSpec } from '../vocabulary'
import { testId, type TestScope } from '../ids'

/** One honest-state banner. Renders the sentence and the next action from vocabulary.ts and nothing
 *  else. Styling belongs to the shell: hook on [data-kind]. The command inside the text sits in <code>. */
export function StateBanner({ route, spec }: { route: TestScope; spec: BannerSpec }) {
  const b = banner(spec)
  const text = bannerText(spec)
  return (
    <div role="status" data-testid={testId(route, 'state-banner')} data-kind={spec.kind} aria-label={text}>
      <span>{b.sentence}</span> <ActionText text={b.action} />
    </div>
  )
}

function ActionText({ text }: { text: string }) {
  const cmd = 'npm run collect'
  const i = text.indexOf(cmd)
  if (i < 0) return <span>{text}</span>
  return (
    <span>
      {text.slice(0, i)}
      <code>{cmd}</code>
      {text.slice(i + cmd.length)}
    </span>
  )
}

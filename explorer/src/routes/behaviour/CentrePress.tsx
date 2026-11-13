// The centre press of the joystick: the ring's one control. Pointer or Space, press and hold; a ring fills
// while it is held. What a hold or a tap does comes from the firmware-rules record, never from here.
import { useEffect } from 'react'
import { testId } from '../../contract'
import type { Behaviour } from './useBehaviour'
import { WORDS } from './model'

const R = 44
const C = 2 * Math.PI * R

export function CentrePress({ b, title, disabled }: { b: Behaviour; title?: string; disabled: boolean }) {
  const { press, release, out } = b
  const h = out.hold
  const frac = h && h.needMs ? Math.min(1, h.heldMs / h.needMs) : 0

  useEffect(() => {
    if (disabled) return
    const ok = (e: KeyboardEvent) => e.code === 'Space' && !e.repeat && (document.activeElement === document.body || (e.target as HTMLElement | null)?.dataset.testid === testId('behaviour', 'joystick-centre'))
    const down = (e: KeyboardEvent) => {
      if (e.code === 'Space' && (document.activeElement === document.body || (e.target as HTMLElement | null)?.dataset.testid === testId('behaviour', 'joystick-centre'))) e.preventDefault()
      if (ok(e)) press('key')
    }
    const up = (e: KeyboardEvent) => {
      if (e.code === 'Space') release('key')
    }
    window.addEventListener('keydown', down)
    window.addEventListener('keyup', up)
    return () => {
      window.removeEventListener('keydown', down)
      window.removeEventListener('keyup', up)
    }
  }, [disabled, press, release])

  return (
      <button
        type="button"
        className="rec-btn"
        data-testid={testId('behaviour', 'joystick-centre')}
        data-pressed={b.pressed ? 'true' : 'false'}
        data-fired={h?.fired ? 'true' : 'false'}
        aria-label={WORDS.centre}
        title={title}
        aria-pressed={b.pressed}
        disabled={disabled}
        onPointerDown={(e) => {
          if (e.button !== 0) return
          e.currentTarget.setPointerCapture(e.pointerId)
          press('pointer')
        }}
        onPointerUp={() => release('pointer')}
        onPointerCancel={() => release('pointer')}
        onKeyDown={(e) => e.key === ' ' && e.preventDefault()}
      >
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <circle className="rec-track" cx="50" cy="50" r={R} />
          <circle className="rec-fill" cx="50" cy="50" r={R} strokeDasharray={C} strokeDashoffset={C * (1 - frac)} data-testid={testId('behaviour', 'hold-progress')} data-frac={frac.toFixed(2)} />
        </svg>
        <span className="rec-dot" />
      </button>
  )
}

// What the screen puts on the shared stage: the "Open the ring" control, the one line on small parts, the
// selected part's tag and, for a made-to-drawing part, the drawing strip. The shell owns the stage element;
// this screen only adds children to it (a portal) and sets one attribute on it that makes room for the strip.
import { useEffect, useLayoutEffect, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { Link } from '../../app/router'
import { testId } from '../../contract'

const stageEl = (): HTMLElement | null => document.querySelector<HTMLElement>('[data-testid="app.stage"]')

/** The shell's stage element, once it is in the page. */
function useStageEl(): HTMLElement | null {
  const [el, setEl] = useState<HTMLElement | null>(null)
  useLayoutEffect(() => setEl(stageEl()), [])
  return el
}

/** Makes room under the ring for the strip: the stage's own box gets a bottom padding that eases. The attribute
 *  starts at 'closed' so that the first change is a transition, never a jump. */
function useSplit(el: HTMLElement | null, split: boolean): void {
  useEffect(() => {
    if (!el) return
    el.dataset.inSplit = 'closed'
    return () => {
      delete el.dataset.inSplit
    }
  }, [el])
  useEffect(() => {
    if (!el) return
    const raf = requestAnimationFrame(() => {
      el.dataset.inSplit = split ? 'open' : 'closed'
    })
    return () => cancelAnimationFrame(raf)
  }, [el, split])
}

/** The word at the slider's start follows the value: closed at 0, open at 1, a percentage between. */
export const stateWord = (v: number): string => (v <= 0.02 ? 'Closed' : v >= 0.98 ? 'Open' : `${Math.round(v * 100)}%`)

export function StageOverlay({ split, ringOpen, onToggle, onAnimate, value, onValue, disabled, tag, onClear, children }: {
  split: boolean
  ringOpen: boolean
  onToggle(): void
  /** animate the one value to an end (0 or 1) */
  onAnimate(v: number): void
  /** the one opening value, 0 closed .. 1 open: the slider shows it and sets it */
  value: number
  onValue(v: number): void
  disabled?: boolean
  /** the selected part: layer and name, or null */
  tag: { layer: string | null; name: string } | null
  onClear(): void
  children: ReactNode
}) {
  const el = useStageEl()
  useSplit(el, split)
  if (!el) return null
  return createPortal(
    <>
      <div className="in-over" data-testid={testId('inside', 'stage-ui')}>
        {tag && (
          <div className="in-tag" data-testid={testId('inside', 'selected-tag')}>
            <span className="label">Selected</span>
            <span className="in-tag-name">{tag.layer ? `${tag.layer} › ${tag.name}` : tag.name}</span>
            <button type="button" aria-label="Clear the selection" data-testid={testId('inside', 'tag-clear')} onClick={onClear}>×</button>
          </div>
        )}
        <div className="in-bar" data-split={split || undefined}>
          {!tag && (
            <p className="in-note" data-testid={testId('inside', 'small-parts-note')}>
              Small board parts such as resistors and capacitors are not drawn in 3D. <Link to="/parts">See them in Parts</Link>
            </p>
          )}
          <button type="button" className="in-end label" disabled={disabled} aria-label="Close the ring" data-testid={testId('inside', 'explode-closed')} onClick={() => onAnimate(0)}>{stateWord(value)}</button>
          <input
            type="range" min={0} max={1} step={0.02} value={value} disabled={disabled} aria-label="Open it up" className="in-slider"
            data-testid={testId('inside', 'explode-slider')} style={{ ['--fill' as string]: `${Math.round(value * 100)}%` }}
            onChange={(e) => onValue(Number(e.target.value))}
          />
          <button type="button" className="in-open label" disabled={disabled} aria-pressed={ringOpen} data-testid={testId('inside', 'open-ring')} onClick={onToggle}>
            {ringOpen ? 'Close the ring' : 'Open the ring'}
          </button>
        </div>
      </div>
      {children}
    </>,
    el,
  )
}

// Bring a block of the panel into view when the owner picks something that opens below the fold.
import { useEffect, useRef, type RefObject } from 'react'

/** Scrolls `ref` into view when `key` changes (not on the first render, and not for key = null). Instant under reduced motion. */
export function useScrollIn(ref: RefObject<HTMLElement | null>, key: string | null): void {
  const seen = useRef(key)
  useEffect(() => {
    if (seen.current === key) return
    seen.current = key
    if (!key) return
    const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ref.current?.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'nearest' })
  }, [key, ref])
}

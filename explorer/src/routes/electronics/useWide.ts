// These two screens are made for a wide panel: the picture takes the main area. The shell offers no way to
// ask for it (docs/lanes/shell.md: "Panel: [data-testid="app.panel-expand"] toggles"), so the screen presses
// that button once after it mounts (after the shell's own reset on a route change). Escape still collapses it.
import { useEffect } from 'react'

export function useWidePanel(): void {
  useEffect(() => {
    const id = window.setTimeout(() => {
      const b = document.querySelector<HTMLButtonElement>('[data-testid="app.panel-expand"]')
      if (b && b.getAttribute('aria-pressed') === 'false') b.click()
    }, 60)
    return () => window.clearTimeout(id)
  }, [])
}

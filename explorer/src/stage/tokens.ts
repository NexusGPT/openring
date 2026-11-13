// Colours the 2D parts of the stage take from the page's tokens (src/styles/tokens.css), with a fallback.
export function cssColour(name: string, fallback: string): string {
  const v = typeof document === 'undefined' ? '' : getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v || fallback
}

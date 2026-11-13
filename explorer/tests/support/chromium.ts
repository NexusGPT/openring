// Finds the Chromium the project already has (Playwright's cache), so no browser is downloaded.
// Override with CHROMIUM_PATH. Returns undefined when none is found (Playwright then uses its own).
import { existsSync, readdirSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'

export function chromiumPath(): string | undefined {
  const fromEnv = process.env.CHROMIUM_PATH
  if (fromEnv) return fromEnv
  const cache = join(homedir(), 'Library', 'Caches', 'ms-playwright')
  if (!existsSync(cache)) return undefined
  const dirs = readdirSync(cache)
    .filter((d) => /^chromium-\d+$/.test(d))
    .sort((a, b) => Number(b.split('-')[1]) - Number(a.split('-')[1]))
  for (const d of dirs) {
    for (const arch of ['chrome-mac-arm64', 'chrome-mac']) {
      const p = join(cache, d, arch, 'Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing')
      if (existsSync(p)) return p
    }
  }
  return undefined
}

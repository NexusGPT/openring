// Self-check of the shared test support: the console watcher sees an error, and the offline blocker
// really stops a request whose host is not 127.0.0.1 (a local server answers on 'localhost', so the
// image loads only if the blocker let it through).
import { expect, test } from '@playwright/test'
import { createServer } from 'node:http'
import type { AddressInfo } from 'node:net'
import { blockOffline, bySuffix, watchConsole } from './page'

const GIF = Buffer.from('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'base64')

test('support: the console watcher and the offline blocker work, headless', async ({ page }) => {
  const server = createServer((_req, res) => {
    res.setHeader('Content-Type', 'image/gif')
    res.setHeader('Access-Control-Allow-Origin', '*')
    res.end(GIF)
  })
  await new Promise<void>((r) => server.listen(0, '127.0.0.1', r))
  const port = (server.address() as AddressInfo).port
  try {
    const w = watchConsole(page)
    await blockOffline(page, w)
    const ext = `http://localhost:${port}/x.gif`
    await page.setContent(
      `<div data-testid="parts.part-card">card</div><script>console.error('boom')</script><img id="ext" src="${ext}">`,
    )
    await expect(bySuffix(page, 'part-card')).toHaveText('card')
    await page.waitForTimeout(400)
    expect(w.errors.some((e) => e.includes('boom'))).toBe(true)
    expect(w.external).toContain(ext)
    expect(await page.evaluate(() => (document.getElementById('ext') as HTMLImageElement).naturalWidth)).toBe(0)
  } finally {
    await new Promise<void>((r) => server.close(() => r()))
  }
})

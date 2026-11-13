// Starts the app for a test that is not run by Playwright's own webServer. It refuses a busy port and
// stops only the process it started.
import { spawn, type ChildProcess } from 'node:child_process'
import { createConnection } from 'node:net'
import { EXPLORER_ROOT } from './bundle'

export function portInUse(port: number, host = '127.0.0.1'): Promise<boolean> {
  return new Promise((res) => {
    const s = createConnection({ port, host })
    s.once('connect', () => (s.destroy(), res(true)))
    s.once('error', () => res(false))
  })
}

export interface RunningApp {
  url: string
  stop(): Promise<void>
}

export async function startApp(opts: { port: number; env?: Record<string, string> }): Promise<RunningApp> {
  if (await portInUse(opts.port)) throw new Error(`port ${opts.port} is busy; nothing was started`)
  const child: ChildProcess = spawn('npx', ['vite', '--port', String(opts.port), '--strictPort'], {
    cwd: EXPLORER_ROOT,
    env: { ...process.env, ...opts.env },
    stdio: 'ignore',
    detached: true,
  })
  const url = `http://127.0.0.1:${opts.port}`
  const deadline = Date.now() + 30_000
  while (Date.now() < deadline) {
    if (await portInUse(opts.port)) break
    await new Promise((r) => setTimeout(r, 200))
  }
  if (!(await portInUse(opts.port))) {
    child.kill()
    throw new Error(`the app did not start on ${opts.port}`)
  }
  return {
    url,
    async stop() {
      if (child.pid) {
        try {
          process.kill(-child.pid)
        } catch {
          /* already gone */
        }
      }
    },
  }
}

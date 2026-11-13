#!/usr/bin/env node
// Runs pytest on a folder with the project's own test venv (.venv-pytest). The design venv has no pytest
// and must not be changed, so the tests get their own: python3 -m venv .venv-pytest && .venv-pytest/bin/pip install pytest
import { existsSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const py = join(root, '.venv-pytest', 'bin', 'pytest')
if (!existsSync(py)) {
  console.error('missing .venv-pytest. Make it once:\n  python3 -m venv .venv-pytest && .venv-pytest/bin/pip install pytest')
  process.exit(2)
}
const r = spawnSync(py, ['-q', ...process.argv.slice(2)], { cwd: root, stdio: 'inherit' })
process.exit(r.status ?? 1)

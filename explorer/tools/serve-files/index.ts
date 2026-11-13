import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { Plugin } from 'vite'
import { createHandler } from './handler.ts'

const explorerRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..')

/** Vite plugin for dev and preview: /data/* from the active bundle, /files/* from the repo root
 *  for the paths listed in files.json only. EXPLORER_BUNDLE picks the bundle (default public/data);
 *  EXPLORER_SOURCE picks the repo root the design files are read from (default: the parent folder). */
export function serveFiles(): Plugin {
  const make = () =>
    createHandler({
      repoRoot: process.env.EXPLORER_SOURCE ? resolve(process.env.EXPLORER_SOURCE) : resolve(explorerRoot, '..'),
      bundleDir: process.env.EXPLORER_BUNDLE ? resolve(process.env.EXPLORER_BUNDLE) : resolve(explorerRoot, 'public', 'data'),
    })
  return {
    name: 'ring-explorer-serve-files',
    configureServer(server) {
      server.middlewares.use(make())
    },
    configurePreviewServer(server) {
      server.middlewares.use(make())
    },
  }
}

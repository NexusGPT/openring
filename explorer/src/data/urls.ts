// Where the app finds its data and files. Every URL is relative to the app's own root, so the same
// build works at / on this Mac and under a sub-path (/ring/) on any static host. No host, no port,
// no absolute path is written in source: the root is read from where this script was loaded.
//   built app   <root>assets/<chunk>.js        -> root = one folder above the chunk
//   dev server  /src/data/urls.ts              -> root = /
const DEV_ROOT = '/'

/** Root URL of the app (always ends with '/'), from the URL of the loaded module. */
export function resolveRoot(moduleUrl: string, dev: boolean): string {
  if (dev) return DEV_ROOT
  return new URL('../', moduleUrl).href
}

export const APP_ROOT: string = resolveRoot(import.meta.url, import.meta.env.DEV)

const encodePath = (p: string): string => p.split('/').map(encodeURIComponent).join('/')
const join = (root: string, rel: string): string => (/^[a-z][a-z0-9+.-]*:/i.test(root) ? new URL(rel, root).href : root + rel)

/** URL of a file in the data bundle: dataUrl('parts.json'), dataUrl('looks/index.json'). */
export function dataUrl(rel: string, root: string = APP_ROOT): string {
  return join(root, `data/${encodePath(rel)}`)
}

/** URL of a design file listed in files.json: fileUrl('design/bom.csv'). Never build /files/... by hand. */
export function fileUrl(path: string, root: string = APP_ROOT): string {
  return join(root, `files/${encodePath(path)}`)
}

/** Basename for the router: '' at the root of a host, '/ring' when hosted under /ring/. */
export function routerBasename(root: string = APP_ROOT): string {
  const p = /^[a-z][a-z0-9+.-]*:/i.test(root) ? new URL(root).pathname : root
  return p.replace(/\/$/, '')
}

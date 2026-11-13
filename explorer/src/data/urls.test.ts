import { describe, expect, it } from 'vitest'
import { dataUrl, fileUrl, resolveRoot, routerBasename } from './urls'

describe('urls relative to the app root', () => {
  it('finds the root of a built app at / and under /ring/', () => {
    expect(resolveRoot('https://h.example/assets/index-1.js', false)).toBe('https://h.example/')
    expect(resolveRoot('https://h.example/ring/assets/index-1.js', false)).toBe('https://h.example/ring/')
    expect(resolveRoot('http://x/src/data/urls.ts', true)).toBe('/')
  })
  it('builds data and file urls under the root, encoding each segment', () => {
    expect(dataUrl('parts.json', '/')).toBe('/data/parts.json')
    expect(dataUrl('looks/index.json', 'https://h.example/ring/')).toBe('https://h.example/ring/data/looks/index.json')
    expect(fileUrl('design/data sheets/a#b.pdf', '/')).toBe('/files/design/data%20sheets/a%23b.pdf')
    expect(fileUrl('design/bom.csv', 'https://h.example/ring/')).toBe('https://h.example/ring/files/design/bom.csv')
  })
  it('gives the router basename', () => {
    expect(routerBasename('/')).toBe('')
    expect(routerBasename('https://h.example/ring/')).toBe('/ring')
  })
})
